"""Profile persistence layer for the profile service."""

from typing import Protocol
from uuid import UUID

import asyncpg

from ..models import ProfileRecord


class ProfileRepositoryProtocol(Protocol):
    """Repository contract used by the profile service."""

    async def ensure_profile_schema(self) -> None:
        """Ensure profile schema is compatible with current service version."""

    async def get_by_user_id(self, user_id: UUID) -> ProfileRecord | None:
        """Return a profile by user identifier, if it exists."""

    async def upsert_profile(
        self,
        user_id: UUID,
        cv_filename: str,
        cv_text: str,
        cv_object_key: str,
        storage_bucket: str,
        desired_role: str | None,
        transition_summary: str | None,
    ) -> ProfileRecord:
        """Insert or update the profile and return its stored representation."""

    async def update_career_goal(
        self,
        user_id: UUID,
        desired_role: str,
        transition_summary: str,
    ) -> ProfileRecord | None:
        """Update career transition data for an existing profile."""

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

    async def ensure_profile_schema(self) -> None:
        """Apply lightweight compatibility changes for existing databases."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            await connection.execute(
                "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS desired_role VARCHAR(120)"
            )
            await connection.execute(
                "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS transition_summary TEXT"
            )

    async def get_by_user_id(self, user_id: UUID) -> ProfileRecord | None:
        """Return a profile by user identifier, if present."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                SELECT id, user_id, cv_filename, cv_text, cv_object_key, storage_bucket,
                       desired_role, transition_summary, created_at, updated_at
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
        desired_role: str | None,
        transition_summary: str | None,
    ) -> ProfileRecord:
        """Create or replace a user profile and return the resulting record."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                INSERT INTO profiles (
                    user_id,
                    cv_filename,
                    cv_text,
                    cv_object_key,
                    storage_bucket,
                    desired_role,
                    transition_summary
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    cv_filename = EXCLUDED.cv_filename,
                    cv_text = EXCLUDED.cv_text,
                    cv_object_key = EXCLUDED.cv_object_key,
                    storage_bucket = EXCLUDED.storage_bucket,
                    desired_role = COALESCE(EXCLUDED.desired_role, profiles.desired_role),
                    transition_summary = COALESCE(EXCLUDED.transition_summary, profiles.transition_summary),
                    updated_at = NOW()
                RETURNING id, user_id, cv_filename, cv_text, cv_object_key, storage_bucket,
                          desired_role, transition_summary, created_at, updated_at
                """,
                user_id,
                cv_filename,
                cv_text,
                cv_object_key,
                storage_bucket,
                desired_role,
                transition_summary,
            )

        if record is None:
            raise RuntimeError("No se pudo guardar el perfil")
        return ProfileRecord.from_record(record)

    async def update_career_goal(
        self,
        user_id: UUID,
        desired_role: str,
        transition_summary: str,
    ) -> ProfileRecord | None:
        """Update career transition fields and return the updated profile."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                UPDATE profiles
                SET desired_role = $2,
                    transition_summary = $3,
                    updated_at = NOW()
                WHERE user_id = $1
                RETURNING id, user_id, cv_filename, cv_text, cv_object_key, storage_bucket,
                          desired_role, transition_summary, created_at, updated_at
                """,
                user_id,
                desired_role,
                transition_summary,
            )

        return ProfileRecord.from_record(record) if record is not None else None
