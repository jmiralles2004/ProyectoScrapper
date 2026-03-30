"""Qdrant storage implementation for integration vectors."""

from typing import Any, Protocol
from uuid import NAMESPACE_URL, UUID, uuid5

from ..models import OfferVectorRecord

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
except ModuleNotFoundError:  # pragma: no cover - handled by runtime configuration
    QdrantClient = None  # type: ignore[assignment]
    qdrant_models = None  # type: ignore[assignment]


class VectorStoreBackendError(Exception):
    """Raised when vector storage operations fail."""


class IntegrationVectorStoreProtocol(Protocol):
    """Vector storage contract used by the integration service."""

    def ensure_collections(self) -> None:
        """Ensure profile and offer collections exist."""

    def upsert_offer(self, offer: OfferVectorRecord, vector: list[float]) -> None:
        """Insert or update an offer vector and payload."""

    def upsert_profile_vector(self, user_id: UUID, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Insert or update a user profile vector."""

    def get_profile_vector(self, user_id: UUID) -> list[float] | None:
        """Return the profile vector associated with a user id."""

    def search_offers(self, query_vector: list[float], limit: int) -> list[OfferVectorRecord]:
        """Search offers by vector similarity."""

    def list_offers(self, limit: int) -> list[OfferVectorRecord]:
        """Return offers stored in the offer collection."""


class QdrantIntegrationVectorStore:
    """Qdrant-backed vector store for Phase 6 integration workflows."""

    def __init__(
        self,
        qdrant_url: str,
        vector_size: int,
        profile_collection: str,
        offer_collection: str,
        timeout_seconds: int = 10,
    ) -> None:
        if QdrantClient is None or qdrant_models is None:
            raise VectorStoreBackendError("qdrant-client dependency is not installed")

        self._vector_size = vector_size
        self._profile_collection = profile_collection
        self._offer_collection = offer_collection
        self._client = QdrantClient(url=qdrant_url, timeout=timeout_seconds)

    def ensure_collections(self) -> None:
        """Create required collections when they do not already exist."""

        try:
            existing = {item.name for item in self._client.get_collections().collections}
            required = [self._profile_collection, self._offer_collection]
            for collection_name in required:
                if collection_name in existing:
                    continue
                self._client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self._vector_size,
                        distance=qdrant_models.Distance.COSINE,
                    ),
                )
        except Exception as exc:
            raise VectorStoreBackendError("Could not ensure required Qdrant collections") from exc

    @staticmethod
    def _offer_point_id(offer_id: str) -> str:
        """Build a deterministic UUID point id from an external offer id."""

        return str(uuid5(NAMESPACE_URL, offer_id))

    @staticmethod
    def _point_vector_to_list(point: Any) -> list[float] | None:
        """Normalize vector payload from Qdrant point structures."""

        vector_payload = getattr(point, "vector", None)
        if vector_payload is None:
            return None
        if isinstance(vector_payload, dict):
            first_value = next(iter(vector_payload.values()), None)
            if first_value is None:
                return None
            return [float(value) for value in first_value]
        return [float(value) for value in vector_payload]

    @staticmethod
    def _build_offer_from_payload(point_id: Any, payload: dict[str, Any] | None, score: float | None) -> OfferVectorRecord:
        """Build an offer record from a Qdrant point payload."""

        data = payload or {}
        return OfferVectorRecord(
            offer_id=str(data.get("offer_id") or point_id),
            title=str(data.get("title") or "Untitled offer"),
            company=str(data.get("company") or "Unknown"),
            description=str(data.get("description") or ""),
            location=data.get("location"),
            apply_url=data.get("apply_url"),
            metadata=dict(data.get("metadata") or {}),
            score=score,
        )

    def upsert_offer(self, offer: OfferVectorRecord, vector: list[float]) -> None:
        """Store one offer vector in the configured offer collection."""

        try:
            self._client.upsert(
                collection_name=self._offer_collection,
                wait=True,
                points=[
                    qdrant_models.PointStruct(
                        id=self._offer_point_id(offer.offer_id),
                        vector=vector,
                        payload={
                            "offer_id": offer.offer_id,
                            "title": offer.title,
                            "company": offer.company,
                            "description": offer.description,
                            "location": offer.location,
                            "apply_url": offer.apply_url,
                            "metadata": offer.metadata,
                        },
                    )
                ],
            )
        except Exception as exc:
            raise VectorStoreBackendError("Could not upsert offer vector in Qdrant") from exc

    def upsert_profile_vector(self, user_id: UUID, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Store one profile vector in the configured profile collection."""

        try:
            self._client.upsert(
                collection_name=self._profile_collection,
                wait=True,
                points=[
                    qdrant_models.PointStruct(
                        id=str(user_id),
                        vector=vector,
                        payload={
                            "user_id": str(user_id),
                            "metadata": metadata or {},
                        },
                    )
                ],
            )
        except Exception as exc:
            raise VectorStoreBackendError("Could not upsert profile vector in Qdrant") from exc

    def get_profile_vector(self, user_id: UUID) -> list[float] | None:
        """Fetch the stored profile vector for a user id."""

        try:
            points = self._client.retrieve(
                collection_name=self._profile_collection,
                ids=[str(user_id)],
                with_vectors=True,
                with_payload=False,
            )
        except Exception as exc:
            raise VectorStoreBackendError("Could not retrieve profile vector from Qdrant") from exc

        if not points:
            return None
        return self._point_vector_to_list(points[0])

    def search_offers(self, query_vector: list[float], limit: int) -> list[OfferVectorRecord]:
        """Search offer vectors using cosine similarity."""

        try:
            hits = self._client.search(
                collection_name=self._offer_collection,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise VectorStoreBackendError("Could not search offers in Qdrant") from exc

        return [
            self._build_offer_from_payload(point_id=hit.id, payload=hit.payload, score=float(hit.score))
            for hit in hits
        ]

    def list_offers(self, limit: int) -> list[OfferVectorRecord]:
        """List offers stored in the vector collection."""

        try:
            points, _ = self._client.scroll(
                collection_name=self._offer_collection,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise VectorStoreBackendError("Could not list offers from Qdrant") from exc

        return [
            self._build_offer_from_payload(point_id=point.id, payload=point.payload, score=None)
            for point in points
        ]
