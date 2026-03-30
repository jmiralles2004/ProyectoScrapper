"""Business logic for the Phase 6 integration workflows."""

import math
from typing import Iterable
from uuid import UUID

from ..models import OfferVectorRecord
from ..vectorstore.qdrant_store import IntegrationVectorStoreProtocol, VectorStoreBackendError


class IntegrationServiceError(Exception):
    """Base class for integration workflow errors."""


class InvalidVectorError(IntegrationServiceError):
    """Raised when vectors are empty or have an invalid size."""


class ProfileVectorNotFoundError(IntegrationServiceError):
    """Raised when a profile vector is missing for a user."""


class IntegrationService:
    """Coordinates offer ingestion and profile-based recommendations."""

    def __init__(
        self,
        vector_store: IntegrationVectorStoreProtocol,
        expected_vector_size: int,
        offer_collection: str,
        profile_collection: str,
    ) -> None:
        self._vector_store = vector_store
        self._expected_vector_size = expected_vector_size
        self._offer_collection = offer_collection
        self._profile_collection = profile_collection

    @property
    def expected_vector_size(self) -> int:
        """Return the configured vector size expected by this service."""

        return self._expected_vector_size

    @property
    def offer_collection(self) -> str:
        """Return the configured offer collection name."""

        return self._offer_collection

    @property
    def profile_collection(self) -> str:
        """Return the configured profile collection name."""

        return self._profile_collection

    def _validate_vector(self, vector: list[float]) -> None:
        """Validate vector content and expected dimensions."""

        if not vector:
            raise InvalidVectorError("El vector no puede estar vacio")
        if len(vector) != self._expected_vector_size:
            raise InvalidVectorError(
                f"El vector debe tener {self._expected_vector_size} dimensiones"
            )
        for value in vector:
            numeric_value = float(value)
            if not math.isfinite(numeric_value):
                raise InvalidVectorError("El vector contiene valores no finitos")

    def import_offers(self, offers: Iterable[tuple[OfferVectorRecord, list[float]]]) -> int:
        """Store offers and vectors in the vector database."""

        imported_count = 0
        try:
            for offer, vector in offers:
                self._validate_vector(vector)
                self._vector_store.upsert_offer(offer=offer, vector=vector)
                imported_count += 1
        except VectorStoreBackendError as exc:
            raise IntegrationServiceError("No se pudieron guardar ofertas en la base vectorial") from exc

        return imported_count

    def import_profile_vector(self, user_id: UUID, vector: list[float], metadata: dict | None = None) -> None:
        """Store one profile vector for recommendation queries."""

        self._validate_vector(vector)
        try:
            self._vector_store.upsert_profile_vector(
                user_id=user_id,
                vector=vector,
                metadata=metadata or {},
            )
        except VectorStoreBackendError as exc:
            raise IntegrationServiceError("No se pudo guardar el vector de perfil") from exc

    def get_recommended_offers(self, user_id: UUID, limit: int) -> list[OfferVectorRecord]:
        """Return offers ranked by similarity against the user profile vector."""

        try:
            profile_vector = self._vector_store.get_profile_vector(user_id)
        except VectorStoreBackendError as exc:
            raise IntegrationServiceError("No se pudo consultar el vector de perfil") from exc

        if profile_vector is None:
            raise ProfileVectorNotFoundError("No existe vector de perfil para este usuario")

        try:
            return self._vector_store.search_offers(query_vector=profile_vector, limit=limit)
        except VectorStoreBackendError as exc:
            raise IntegrationServiceError("No se pudieron calcular recomendaciones") from exc

    def list_offer_catalog(self, limit: int) -> list[OfferVectorRecord]:
        """Return offer catalog currently available in the vector database."""

        try:
            return self._vector_store.list_offers(limit=limit)
        except VectorStoreBackendError as exc:
            raise IntegrationServiceError("No se pudo listar el catalogo de ofertas") from exc
