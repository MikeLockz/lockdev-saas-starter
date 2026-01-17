from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Lockdev SaaS Starter"
    ENVIRONMENT: str = "local"
    SENTRY_DSN: str | None = None

    # Database
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "devpassword"  # - dev default
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 54320

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]
    ALLOWED_DOMAINS: list[str] = [
        "localhost",
        "127.0.0.1",
        "identitytoolkit.googleapis.com",
        "securetoken.googleapis.com",
        "api.stripe.com",
    ]
    FRONTEND_URL: str = "http://localhost:5173"

    # Security
    SESSION_SECRET: str = "changeme"  # - dev default

    # AWS
    AWS_REGION: str = "us-east-1"

    # Stripe
    STRIPE_API_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_SUCCESS_URL: str = "http://localhost:5173/billing/success"
    STRIPE_CANCEL_URL: str = "http://localhost:5173/billing/cancel"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
