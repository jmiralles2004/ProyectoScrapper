"""Application settings for the profile service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    minio_endpoint: str
    minio_root_user: str
    minio_root_password: str
    minio_bucket_profiles: str = "profiles"
    minio_secure: bool = False
    ocr_enabled: bool = True
    ocr_languages: str = "spa+eng"
    ocr_dpi: int = 300
    service_name: str = "profile-service"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from the environment."""

    return Settings()
