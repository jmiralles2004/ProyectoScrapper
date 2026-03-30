"""Application settings for the integration service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    qdrant_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    integration_vector_size: int = 384
    qdrant_collection_profiles: str = "profile_vectors"
    qdrant_collection_offers: str = "offer_vectors"
    integration_ingest_api_key: str = ""
    service_name: str = "integration-service"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from the environment."""

    return Settings()
