import uuid
from contextlib import asynccontextmanager

import secure
import sentry_sdk
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin import setup_admin
from src.api import admin, consent, events, organizations, telemetry, users, webhooks, invitations, patients, providers, staff, appointments, documents, proxies, billing, notifications, messaging, calls, tasks, support
from src.config import settings
from src.database import engine, get_db
from src.logging import configure_logging, request_id_ctx
from src.middleware.audit import AuditMiddleware

# Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN, 
        environment=settings.ENVIRONMENT,
        send_default_pii=False,
    )

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Secure Headers
secure_headers = secure.Secure.with_default_headers()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    configure_logging()
    yield
    # Shutdown
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Admin Interface
setup_admin(app, engine)

app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(consent.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users") # Wait, checking users registration again.
app.include_router(organizations.router, prefix=f"{settings.API_V1_STR}/organizations")
app.include_router(patients.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/patients", tags=["patients"])
app.include_router(providers.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/providers", tags=["providers"])
app.include_router(staff.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/staff", tags=["staff"])
app.include_router(appointments.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/appointments", tags=["appointments"])
app.include_router(documents.router, prefix=settings.API_V1_STR, tags=["documents"])
app.include_router(invitations.router, prefix=f"{settings.API_V1_STR}/invitations")
app.include_router(proxies.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/patients/{{patient_id}}/proxies", tags=["proxies"])
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router, prefix=settings.API_V1_STR)
app.include_router(billing.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/billing", tags=["billing"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/users/me/notifications", tags=["notifications"])
app.include_router(messaging.router, prefix=f"{settings.API_V1_STR}/users/me/threads", tags=["messaging"])
app.include_router(calls.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/calls", tags=["calls"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/organizations/{{org_id}}/tasks", tags=["tasks"])
app.include_router(tasks.user_tasks_router, prefix=f"{settings.API_V1_STR}/users/tasks", tags=["tasks"])
app.include_router(support.router, prefix=f"{settings.API_V1_STR}/support", tags=["support"])



# 1. TrustedHostMiddleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Security Headers (Custom Middleware Wrapper)
@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    return response

# 4. Request ID (Custom Middleware)
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_ctx.reset(token)

# 5. Audit Middleware (Read Access Logging)
app.add_middleware(AuditMiddleware)

# 6. SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 7. GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/health/deep")
async def deep_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {"status": "ok", "db": db_status, "redis": "unknown"}
