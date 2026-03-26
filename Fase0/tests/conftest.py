"""
Shared pytest fixtures for JobMatch infrastructure tests.

Loads service connection parameters from the .env file located at the
project root (one level above this tests/ directory).
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env from project root so tests can run without exporting env vars
_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / ".env")


# ── Connection parameter fixtures ───────────────────────────────────────────

@pytest.fixture(scope="session")
def postgres_dsn() -> str:
    """Return the asyncpg-compatible DSN for PostgreSQL."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB", "jobmatch")
    user = os.getenv("POSTGRES_USER", "jobmatch_user")
    pwd  = os.getenv("POSTGRES_PASSWORD", "jobmatch_pass")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


@pytest.fixture(scope="session")
def redis_params() -> dict:
    """Return redis-py connection kwargs."""
    return {
        "host":     os.getenv("REDIS_HOST", "localhost"),
        "port":     int(os.getenv("REDIS_PORT", "6379")),
        "password": os.getenv("REDIS_PASSWORD", "redis_pass"),
        "decode_responses": True,
    }


@pytest.fixture(scope="session")
def minio_params() -> dict:
    """Return Minio client constructor kwargs."""
    return {
        "endpoint":   os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.getenv("MINIO_ROOT_USER", "minioadmin"),
        "secret_key": os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123"),
        "secure":     False,
    }


@pytest.fixture(scope="session")
def qdrant_url() -> str:
    """Return the Qdrant HTTP base URL."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = os.getenv("QDRANT_PORT", "6333")
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def nginx_url() -> str:
    """Return the Nginx proxy base URL."""
    port = os.getenv("NGINX_PORT", "80")
    return f"http://localhost:{port}"
