"""Request and response schemas for the integration service."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str
    service: str


class OfferImportItem(BaseModel):
    """Offer payload including vector information."""

    offer_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=20000)
    location: str | None = Field(default=None, max_length=255)
    apply_url: str | None = Field(default=None, max_length=1000)
    vector: list[float] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OffersImportRequest(BaseModel):
    """Batch payload to import offers into the vector database."""

    offers: list[OfferImportItem] = Field(min_length=1)


class OffersImportResponse(BaseModel):
    """Response returned after importing offers."""

    imported_offers: int
    collection: str
    vector_size: int


class ProfileVectorImportRequest(BaseModel):
    """Payload used to register a user profile vector."""

    user_id: UUID
    vector: list[float] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProfileVectorImportResponse(BaseModel):
    """Response returned after storing a profile vector."""

    user_id: UUID
    collection: str
    vector_size: int


class OfferResponse(BaseModel):
    """Offer payload returned by catalog and recommendation endpoints."""

    offer_id: str
    title: str
    company: str
    description: str
    location: str | None = None
    apply_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class OfferCatalogResponse(BaseModel):
    """Offer catalog response."""

    collection: str
    total: int
    offers: list[OfferResponse]


class RecommendedOffersResponse(BaseModel):
    """Recommendations tailored to the authenticated user profile."""

    user_id: UUID
    collection: str
    total: int
    offers: list[OfferResponse]
