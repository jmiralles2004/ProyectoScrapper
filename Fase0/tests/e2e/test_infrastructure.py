"""
Infrastructure connectivity tests for JobMatch FASE 0.

Each test verifies that a service is reachable and behaves correctly.
These tests must be run after `docker compose up -d` with all services healthy.

Run:
    pytest tests/e2e/test_infrastructure.py -v
"""

import asyncio

import asyncpg
import httpx
import pytest
import redis as redis_lib
from minio import Minio
from qdrant_client import QdrantClient


# ── PostgreSQL ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_postgres_connection(postgres_dsn: str) -> None:
    """Verify that PostgreSQL accepts connections and responds to SELECT 1."""
    conn = await asyncpg.connect(postgres_dsn)
    try:
        result: int = await conn.fetchval("SELECT 1")
        assert result == 1, "Expected SELECT 1 to return 1"
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_pgvector_extension(postgres_dsn: str) -> None:
    """Verify that the pgvector extension is installed in the database."""
    conn = await asyncpg.connect(postgres_dsn)
    try:
        row = await conn.fetchrow(
            "SELECT extname FROM pg_extension WHERE extname = 'vector'"
        )
        assert row is not None, "pgvector extension is not installed"
        assert row["extname"] == "vector"
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_users_table_exists(postgres_dsn: str) -> None:
    """Verify that the users table was created by init-db.sql."""
    conn = await asyncpg.connect(postgres_dsn)
    try:
        row = await conn.fetchrow(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'users'
            """
        )
        assert row is not None, "users table does not exist"
    finally:
        await conn.close()


# ── Redis ────────────────────────────────────────────────────────────────────

def test_redis_connection(redis_params: dict) -> None:
    """Verify that Redis accepts connections and responds to PING."""
    client = redis_lib.Redis(**redis_params)
    try:
        response = client.ping()
        assert response is True, "Redis did not respond to PING"
    finally:
        client.close()


def test_redis_set_get(redis_params: dict) -> None:
    """Verify basic SET/GET round-trip on Redis."""
    client = redis_lib.Redis(**redis_params)
    try:
        client.set("jobmatch:healthcheck", "ok", ex=10)
        value = client.get("jobmatch:healthcheck")
        assert value == "ok", f"Unexpected value from Redis GET: {value!r}"
    finally:
        client.delete("jobmatch:healthcheck")
        client.close()


# ── MinIO ────────────────────────────────────────────────────────────────────

def test_minio_connection(minio_params: dict) -> None:
    """Verify that MinIO is reachable and the client can list buckets."""
    client = Minio(**minio_params)
    buckets = client.list_buckets()
    # A fresh MinIO instance returns an empty list – that is still a valid response
    assert isinstance(buckets, list), "Expected list_buckets() to return a list"


def test_minio_bucket_create_delete(minio_params: dict) -> None:
    """Verify that a bucket can be created and removed in MinIO."""
    client = Minio(**minio_params)
    bucket = "jobmatch-test-bucket"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    assert client.bucket_exists(bucket), "Bucket was not created"
    client.remove_bucket(bucket)
    assert not client.bucket_exists(bucket), "Bucket was not removed"


# ── Qdrant ───────────────────────────────────────────────────────────────────

def test_qdrant_connection(qdrant_url: str) -> None:
    """Verify that Qdrant is reachable and returns its collection list."""
    client = QdrantClient(url=qdrant_url)
    collections = client.get_collections()
    assert hasattr(collections, "collections"), (
        "Unexpected response from Qdrant get_collections()"
    )


# ── Nginx ────────────────────────────────────────────────────────────────────

def test_nginx_health(nginx_url: str) -> None:
    """Verify that the Nginx /health endpoint returns HTTP 200."""
    response = httpx.get(f"{nginx_url}/health", timeout=5.0)
    assert response.status_code == 200, (
        f"Expected 200 from /health, got {response.status_code}"
    )
    body = response.json()
    assert body.get("status") == "ok", f"Unexpected health body: {body}"


def test_nginx_unknown_route_returns_404(nginx_url: str) -> None:
    """Verify that unknown routes return 404 (not a 5xx)."""
    response = httpx.get(f"{nginx_url}/non-existent-route", timeout=5.0)
    assert response.status_code == 404, (
        f"Expected 404 for unknown route, got {response.status_code}"
    )
