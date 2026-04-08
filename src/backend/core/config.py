from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Centralized Configuration singleton loading secrets natively from `.env`.
    Manages API mappings, PostgreSQL connections, and Redis networking.
    """
    PROJECT_NAME: str = "File Sorter Enterprise API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str  # Generates 256-bit hashes, e.g. using: openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days validity
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "filesorter_db"
    DATABASE_URL: Optional[str] = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
if not settings.DATABASE_URL:
    settings.DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"