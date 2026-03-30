"""Application settings for the auth service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    service_name: str = "auth-service"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from the environment."""

    return Settings()
