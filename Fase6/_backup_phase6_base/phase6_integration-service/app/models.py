"""Internal data models used by the integration service."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OfferVectorRecord:
    """Offer metadata stored as payload in the vector database."""

    offer_id: str
    title: str
    company: str
    description: str
    location: str | None = None
    apply_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float | None = None
