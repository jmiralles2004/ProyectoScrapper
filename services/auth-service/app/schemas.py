"""Request and response schemas for the auth service."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr = Field(
        description="Email unico del usuario. Se normaliza a minusculas.",
        examples=["ana@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contrasena en texto plano (minimo 8 caracteres).",
        examples=["MiClaveSegura123"],
    )


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr = Field(
        description="Email de una cuenta ya registrada.",
        examples=["ana@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Contrasena de la cuenta registrada.",
        examples=["MiClaveSegura123"],
    )


class UserRead(BaseModel):
    """Public user response without sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Identificador unico del usuario.")
    email: EmailStr = Field(description="Email publico del usuario.")
    is_active: bool = Field(description="Indica si la cuenta esta activa.")
    created_at: datetime = Field(description="Fecha/hora UTC de creacion de la cuenta.")
    updated_at: datetime = Field(description="Fecha/hora UTC de la ultima actualizacion.")


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str = Field(
        description="JWT de acceso para autenticar llamadas a endpoints protegidos.",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token HTTP Authorization.",
        examples=["bearer"],
    )


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str = Field(description="Estado del servicio, normalmente `ok`.", examples=["ok"])
    service: str = Field(description="Nombre logico del servicio que responde.")
