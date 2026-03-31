"""Request and response schemas for the profile service."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str = Field(description="Estado del servicio, normalmente `ok`.", examples=["ok"])
    service: str = Field(description="Nombre del servicio que responde.")


class ProfileUploadResponse(BaseModel):
    """Response returned after uploading a CV."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID interno del perfil almacenado.")
    user_id: UUID = Field(description="ID del usuario dueno del perfil.")
    cv_filename: str = Field(description="Nombre original del archivo PDF subido.")
    cv_object_key: str = Field(description="Ruta/clave del objeto guardado en MinIO.")
    storage_bucket: str = Field(description="Bucket donde se persiste el perfil.")
    extracted_text_length: int = Field(
        description="Cantidad de caracteres extraidos y normalizados del CV.",
    )
    created_at: datetime = Field(description="Fecha/hora UTC de creacion del perfil.")
    updated_at: datetime = Field(description="Fecha/hora UTC de la ultima actualizacion.")


class ProfileReadResponse(ProfileUploadResponse):
    """Response returned when fetching the current profile."""

    cv_text_preview: str = Field(
        default="",
        max_length=500,
        description="Vista previa corta del texto extraido del CV.",
    )
