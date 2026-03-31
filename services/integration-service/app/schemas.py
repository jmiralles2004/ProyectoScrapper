"""Request and response schemas for the integration service."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str = Field(description="Estado del servicio, normalmente `ok`.", examples=["ok"])
    service: str = Field(description="Nombre del servicio que responde.")


class OfferImportItem(BaseModel):
    """Offer payload including vector information."""

    offer_id: str = Field(
        min_length=1,
        max_length=120,
        description="ID unico de la oferta en el sistema origen.",
        examples=["offer-123"],
    )
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Titulo visible de la vacante.",
        examples=["Backend Python Engineer"],
    )
    company: str = Field(
        min_length=1,
        max_length=255,
        description="Nombre de la empresa contratante.",
        examples=["Acme Tech"],
    )
    description: str = Field(
        min_length=1,
        max_length=20000,
        description="Descripcion textual de responsabilidades y requisitos.",
    )
    location: str | None = Field(
        default=None,
        max_length=255,
        description="Ubicacion de la oferta (opcional).",
        examples=["Madrid, ES"],
    )
    apply_url: str | None = Field(
        default=None,
        max_length=1000,
        description="URL de postulacion (opcional).",
        examples=["https://jobs.example.com/offer-123"],
    )
    vector: list[float] = Field(
        min_length=1,
        description="Embedding de la oferta. Debe coincidir con el tamano configurado.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos adicionales libres para filtrado/auditoria.",
    )


class OffersImportRequest(BaseModel):
    """Batch payload to import offers into the vector database."""

    offers: list[OfferImportItem] = Field(
        min_length=1,
        description="Lote de ofertas a importar.",
    )


class OffersImportResponse(BaseModel):
    """Response returned after importing offers."""

    imported_offers: int = Field(description="Cantidad total de ofertas importadas exitosamente.")
    collection: str = Field(description="Nombre de la coleccion de ofertas en Qdrant.")
    vector_size: int = Field(description="Tamano vectorial esperado por la coleccion.")


class ProfileVectorImportRequest(BaseModel):
    """Payload used to register a user profile vector."""

    user_id: UUID = Field(description="ID del usuario al que pertenece el vector de perfil.")
    vector: list[float] = Field(
        min_length=1,
        description="Embedding del perfil del usuario. Debe cumplir el tamano configurado.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos opcionales asociados al vector de perfil.",
    )


class ProfileVectorImportResponse(BaseModel):
    """Response returned after storing a profile vector."""

    user_id: UUID = Field(description="ID del usuario cuyo vector fue importado.")
    collection: str = Field(description="Nombre de la coleccion de perfiles en Qdrant.")
    vector_size: int = Field(description="Tamano vectorial esperado por la coleccion.")


class OfferResponse(BaseModel):
    """Offer payload returned by catalog and recommendation endpoints."""

    offer_id: str = Field(description="ID unico de la oferta.")
    title: str = Field(description="Titulo de la oferta.")
    company: str = Field(description="Empresa de la oferta.")
    description: str = Field(description="Descripcion de la vacante.")
    location: str | None = Field(default=None, description="Ubicacion de la oferta.")
    apply_url: str | None = Field(default=None, description="URL para postular (si existe).")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales.")
    score: float | None = Field(
        default=None,
        description="Score de similitud; aparece en endpoints de recomendacion.",
    )


class OfferCatalogResponse(BaseModel):
    """Offer catalog response."""

    collection: str = Field(description="Coleccion consultada en la base vectorial.")
    total: int = Field(description="Numero de ofertas devueltas en esta respuesta.")
    offers: list[OfferResponse] = Field(description="Listado de ofertas disponibles.")


class RecommendedOffersResponse(BaseModel):
    """Recommendations tailored to the authenticated user profile."""

    user_id: UUID = Field(description="Usuario autenticado para el que se calcularon recomendaciones.")
    collection: str = Field(description="Coleccion de ofertas usada para el ranking semantico.")
    total: int = Field(description="Numero de recomendaciones incluidas en esta respuesta.")
    offers: list[OfferResponse] = Field(description="Ofertas ordenadas por relevancia semantica.")
