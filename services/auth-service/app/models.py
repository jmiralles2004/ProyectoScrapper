"""Internal data models used by the auth service."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Record


@dataclass(slots=True)
class UserRecord:
    """Database representation of a user."""

    id: UUID
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: Record) -> "UserRecord":
        """Build a user model from an asyncpg record."""

        return cls(
            id=record["id"],
            email=record["email"],
            hashed_password=record["hashed_password"],
            is_active=record["is_active"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
