"""User persistence for the auth service."""

from typing import Protocol
from uuid import UUID

import asyncpg

from ..models import UserRecord


class UserRepositoryProtocol(Protocol):
    """Repository contract used by the auth service."""

    async def get_by_email(self, email: str) -> UserRecord | None:
        """Return a user by email, if it exists."""

    async def get_by_id(self, user_id: UUID) -> UserRecord | None:
        """Return a user by identifier, if it exists."""

    async def create_user(self, email: str, hashed_password: str) -> UserRecord:
        """Create and return a new user."""

    async def close(self) -> None:
        """Release any open resources."""


class PostgresUserRepository:
    """Async PostgreSQL implementation for users."""

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

    async def get_by_email(self, email: str) -> UserRecord | None:
        """Return a user by email, if present."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                SELECT id, email, hashed_password, is_active, created_at, updated_at
                FROM users
                WHERE email = $1
                """,
                email,
            )
        return UserRecord.from_record(record) if record is not None else None

    async def get_by_id(self, user_id: UUID) -> UserRecord | None:
        """Return a user by identifier, if present."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                SELECT id, email, hashed_password, is_active, created_at, updated_at
                FROM users
                WHERE id = $1
                """,
                user_id,
            )
        return UserRecord.from_record(record) if record is not None else None

    async def create_user(self, email: str, hashed_password: str) -> UserRecord:
        """Insert a new user and return the stored record."""

        pool = await self._get_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                INSERT INTO users (email, hashed_password)
                VALUES ($1, $2)
                RETURNING id, email, hashed_password, is_active, created_at, updated_at
                """,
                email,
                hashed_password,
            )
        if record is None:
            raise RuntimeError("No se pudo crear el usuario")
        return UserRecord.from_record(record)
