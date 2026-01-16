from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import configure_logging
from app.core.config import settings
from app.api.health import router as health_router
import structlog

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # In a real app, json_logs would come from settings
    configure_logging(json_logs=True) 
    logger.info("Application started")
    yield
    logger.info("Application shutdown")

app = FastAPI(title="Lockdev SaaS Starter", lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router, prefix="/api/v1")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}