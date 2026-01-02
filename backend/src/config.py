from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", "../.env"], env_ignore_empty=True, extra="ignore")

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Lockdev SaaS"

    ENVIRONMENT: str = "local"
    SENTRY_DSN: str | None = None

    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str

    # Google Cloud / Vertex AI
    GOOGLE_CLOUD_PROJECT: str = "lockdev-saas"  # Default for local dev
    GOOGLE_CLOUD_LOCATION: str = "us-central1"  # Default region for Vertex AI

    # AWS Telephony
    AWS_PINPOINT_APPLICATION_ID: str = ""  # Required for SMS
    AWS_CONNECT_INSTANCE_ID: str = ""  # Required for calls
    AWS_CONNECT_CONTACT_FLOW_ID: str = ""  # Default flow for outbound calls

    # AWS S3
    AWS_S3_BUCKET: str = ""  # Document storage bucket
    AWS_REGION: str = "us-west-2"  # AWS region

    # Stripe Billing
    STRIPE_API_KEY: str = ""  # Stripe secret key (sk_test_... or sk_live_...)
    STRIPE_WEBHOOK_SECRET: str = ""  # Webhook endpoint signing secret (whsec_...)
    STRIPE_SUCCESS_URL: str = "http://localhost:5173/billing/success"
    STRIPE_CANCEL_URL: str = "http://localhost:5173/billing/cancel"

    # Parse Redis URL for ARQ worker
    @property
    def REDIS_HOST(self) -> str:
        """Extract Redis host from REDIS_URL"""
        from urllib.parse import urlparse

        parsed = urlparse(self.REDIS_URL)
        return parsed.hostname or "localhost"

    @property
    def REDIS_PORT(self) -> int:
        """Extract Redis port from REDIS_URL"""
        from urllib.parse import urlparse

        parsed = urlparse(self.REDIS_URL)
        return parsed.port or 6379

    @property
    def REDIS_DB(self) -> int:
        """Extract Redis database from REDIS_URL"""
        from urllib.parse import urlparse

        parsed = urlparse(self.REDIS_URL)
        # Database is the path without leading slash
        if parsed.path and len(parsed.path) > 1:
            return int(parsed.path[1:])
        return 0

    # Security
    SECRET_KEY: str

    # CORS & Security
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    FRONTEND_URL: str = "http://localhost:5173"

    @computed_field
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        return [self.FRONTEND_URL]


settings = Settings()
