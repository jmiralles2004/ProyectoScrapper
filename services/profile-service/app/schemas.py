"""Request and response schemas for the profile service."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str
    service: str


class ProfileUploadResponse(BaseModel):
    """Response returned after uploading a CV."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    cv_filename: str
    cv_object_key: str
    storage_bucket: str
    extracted_text_length: int
    created_at: datetime
    updated_at: datetime


class ProfileReadResponse(ProfileUploadResponse):
    """Response returned when fetching the current profile."""

    cv_text_preview: str = Field(default="", max_length=500)
