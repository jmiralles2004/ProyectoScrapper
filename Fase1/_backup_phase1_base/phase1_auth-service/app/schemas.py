"""Request and response schemas for the auth service."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    """Public user response without sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str
    service: str
