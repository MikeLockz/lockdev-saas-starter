from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from secure import Secure
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.api import (
    admin,
    consent,
    documents,
    events,
    health,
    invitations,
    organizations,
    patients,
    telemetry,
    users,
    webhooks,
)
from app.core.auth import require_hipaa_consent
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.core.middleware import (
    ContextMiddleware,
    ReadAuditMiddleware,
    RequestIDMiddleware,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup logic
    configure_logging(json_logs=(settings.ENVIRONMENT != "local"))
    logger.info("Starting up", environment=settings.ENVIRONMENT)
    yield
    # Shutdown logic
    logger.info("Shutting down")


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=1.0,
    )


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# Admin Panel
setup_admin(app)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# Security Headers
secure_headers = Secure.with_default_headers()


@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    return response


# Standard Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ContextMiddleware)
app.add_middleware(ReadAuditMiddleware)

if settings.SESSION_SECRET == "changeme":  # noqa: S105
    if settings.ENVIRONMENT != "local":
        logger.warning(
            "CRITICAL: Using default SESSION_SECRET in non-local environment!"
        )
    else:
        logger.warning("Using default SESSION_SECRET (safe for local dev)")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=(settings.ENVIRONMENT != "local"),
)


# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(consent.router, prefix="/api/consent", tags=["Consent"])
app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["Documents"],
    dependencies=[Depends(require_hipaa_consent)],
)
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(
    organizations.router, prefix="/api/organizations", tags=["Organizations"]
)
app.include_router(invitations.router, prefix="/api/invitations", tags=["Invitations"])
app.include_router(
    patients.router,
    prefix="/api/organizations",
    tags=["Patients"],
    dependencies=[Depends(require_hipaa_consent)],
)


@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    logger.info("Root endpoint called", path=request.url.path)
    return {"message": "Hello World"}
