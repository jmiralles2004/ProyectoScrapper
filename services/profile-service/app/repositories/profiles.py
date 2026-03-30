"""Profile persistence layer for the profile service."""

from typing import Protocol
from uuid import UUID

import asyncpg

from ..models import ProfileRecord


class ProfileRepositoryProtocol(Protocol):
    """Repository contract used by the profile service."""

    async def get_by_user_id(self, user_id: UUID) -> ProfileRecord | None:
        """Return a profile by user identifier, if it exists."""

    async def upsert_profile(
        self,
        user_id: UUID,
        cv_filename: str,
        cv_text: str,
        cv_object_key: str,
        storage_bucket: str,
    ) -> ProfileRecord:
        """Insert or update the profile and return its stored representation."""

    async def close(self) -> None:
        """Release any open resources."""


class PostgresProfileRepository:
    """Async PostgreSQL implementation for profiles."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Create the connection pool on demand."""

        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self._database_url,
                min_size=1,
                max_size=5,
            )
        return self._pool

    async def close(self) -> None:
        """Close the connection pool if it exists."""

        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def get_by_user_id(self, user_id: UUID) -> ProfileRecord | None:
        """Return a profile by user identifier, if present."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                SELECT id, user_id, cv_filename, cv_text, cv_object_key, storage_bucket, created_at, updated_at
                FROM profiles
                WHERE user_id = $1
                """,
                user_id,
            )
        return ProfileRecord.from_record(record) if record is not None else None

    async def upsert_profile(
        self,
        user_id: UUID,
        cv_filename: str,
        cv_text: str,
        cv_object_key: str,
        storage_bucket: str,
    ) -> ProfileRecord:
        """Create or replace a user profile and return the resulting record."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                INSERT INTO profiles (user_id, cv_filename, cv_text, cv_object_key, storage_bucket)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    cv_filename = EXCLUDED.cv_filename,
                    cv_text = EXCLUDED.cv_text,
                    cv_object_key = EXCLUDED.cv_object_key,
                    storage_bucket = EXCLUDED.storage_bucket,
                    updated_at = NOW()
                RETURNING id, user_id, cv_filename, cv_text, cv_object_key, storage_bucket, created_at, updated_at
                """,
                user_id,
                cv_filename,
                cv_text,
                cv_object_key,
                storage_bucket,
            )

        if record is None:
            raise RuntimeError("No se pudo guardar el perfil")
        return ProfileRecord.from_record(record)
