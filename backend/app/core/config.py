from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lockdev SaaS Starter"
    ENVIRONMENT: str = "local"
    
    # Database
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "devpassword"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 54320
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
