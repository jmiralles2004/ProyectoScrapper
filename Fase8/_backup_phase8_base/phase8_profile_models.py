"""Internal data models used by the profile service."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Record


@dataclass(slots=True)
class ProfileRecord:
    """Database representation of a profile."""

    id: UUID
    user_id: UUID
    cv_filename: str
    cv_text: str
    cv_object_key: str
    storage_bucket: str
    desired_role: str | None
    transition_summary: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: Record) -> "ProfileRecord":
        """Build a profile model from an asyncpg record."""

        return cls(
            id=record["id"],
            user_id=record["user_id"],
            cv_filename=record["cv_filename"],
            cv_text=record["cv_text"],
            cv_object_key=record["cv_object_key"],
            storage_bucket=record["storage_bucket"],
            desired_role=record["desired_role"],
            transition_summary=record["transition_summary"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
