"""Unit tests for the integration service."""

from datetime import datetime, timedelta, timezone
from math import sqrt
from typing import Any
from uuid import UUID, uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.models import OfferVectorRecord
from app.services.integration import IntegrationService


class FakeVectorStore:
    """In-memory vector store used in integration service tests."""

    def __init__(self) -> None:
        self.offers: dict[str, tuple[OfferVectorRecord, list[float]]] = {}
        self.profile_vectors: dict[str, list[float]] = {}

    def ensure_collections(self) -> None:
        return None

    def upsert_offer(self, offer: OfferVectorRecord, vector: list[float]) -> None:
        self.offers[offer.offer_id] = (offer, list(vector))

    def upsert_profile_vector(self, user_id: UUID, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        self.profile_vectors[str(user_id)] = list(vector)

    def get_profile_vector(self, user_id: UUID) -> list[float] | None:
        vector = self.profile_vectors.get(str(user_id))
        return list(vector) if vector is not None else None

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = sqrt(sum(a * a for a in left))
        right_norm = sqrt(sum(b * b for b in right))
        if left_norm == 0.0 or right_norm == 0.0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def search_offers(self, query_vector: list[float], limit: int) -> list[OfferVectorRecord]:
        scored: list[OfferVectorRecord] = []
        for offer, vector in self.offers.values():
            scored.append(
                OfferVectorRecord(
                    offer_id=offer.offer_id,
                    title=offer.title,
                    company=offer.company,
                    description=offer.description,
                    location=offer.location,
                    apply_url=offer.apply_url,
                    metadata=offer.metadata,
                    score=self._cosine_similarity(query_vector, vector),
                )
            )

        scored.sort(key=lambda item: item.score or 0.0, reverse=True)
        return scored[:limit]

    def list_offers(self, limit: int) -> list[OfferVectorRecord]:
        return [item[0] for item in list(self.offers.values())[:limit]]


def build_token(user_id: UUID) -> str:
    """Create a JWT token for a fake authenticated user."""

    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(hours=1),
    }
    return jwt.encode(payload, "test-secret", algorithm="HS256")


def auth_headers(user_id: UUID) -> dict[str, str]:
    """Build authorization headers for tests."""

    return {"Authorization": f"Bearer {build_token(user_id)}"}


def build_client() -> TestClient:
    """Create an integration service test client with fake vector storage."""

    settings = Settings(
        qdrant_url="http://localhost:6333",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        integration_vector_size=4,
        qdrant_collection_profiles="profile_vectors",
        qdrant_collection_offers="offer_vectors",
        integration_ingest_api_key="ingest-secret",
        service_name="integration-service",
    )

    app = create_app(settings)
    vector_store = FakeVectorStore()
    app.state.vector_store = vector_store
    app.state.integration_service = IntegrationService(
        vector_store=vector_store,
        expected_vector_size=4,
        offer_collection="offer_vectors",
        profile_collection="profile_vectors",
    )
    return TestClient(app)


def test_healthcheck_returns_service_name() -> None:
    """Health endpoints should confirm the integration service is running."""

    with build_client() as client:
        response = client.get("/health")
        routed_response = client.get("/integration/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "integration-service"}
    assert routed_response.status_code == 200


def test_import_requires_internal_api_key() -> None:
    """Ingestion endpoints should reject requests without internal API key."""

    with build_client() as client:
        response = client.post(
            "/integration/offers/import",
            json={
                "offers": [
                    {
                        "offer_id": "offer-1",
                        "title": "Backend Developer",
                        "company": "Acme",
                        "description": "Python role",
                        "vector": [1.0, 0.0, 0.0, 0.0],
                    }
                ]
            },
        )

    assert response.status_code == 401


def test_import_offers_and_list_catalog() -> None:
    """Imported offers should be available through the catalog endpoint."""

    with build_client() as client:
        import_response = client.post(
            "/integration/offers/import",
            headers={"x-internal-api-key": "ingest-secret"},
            json={
                "offers": [
                    {
                        "offer_id": "offer-1",
                        "title": "Backend Developer",
                        "company": "Acme",
                        "description": "Python role",
                        "vector": [1.0, 0.0, 0.0, 0.0],
                    },
                    {
                        "offer_id": "offer-2",
                        "title": "Data Analyst",
                        "company": "DataCorp",
                        "description": "Analytics role",
                        "vector": [0.2, 0.8, 0.0, 0.0],
                    },
                ]
            },
        )

        assert import_response.status_code == 201
        assert import_response.json()["imported_offers"] == 2

        catalog_response = client.get(
            "/integration/offers/catalog",
            headers={"x-internal-api-key": "ingest-secret"},
        )

    assert catalog_response.status_code == 200
    assert catalog_response.json()["total"] == 2


def test_recommended_offers_requires_bearer_token() -> None:
    """Recommendation endpoint should enforce JWT authentication."""

    with build_client() as client:
        response = client.get("/integration/offers/recommended")

    assert response.status_code == 401


def test_recommendations_flow_uses_profile_vector_similarity() -> None:
    """Recommendations should be sorted by similarity against profile vector."""

    user_id = uuid4()

    with build_client() as client:
        import_response = client.post(
            "/integration/offers/import",
            headers={"x-internal-api-key": "ingest-secret"},
            json={
                "offers": [
                    {
                        "offer_id": "offer-1",
                        "title": "Python Engineer",
                        "company": "Acme",
                        "description": "Backend Python",
                        "vector": [1.0, 0.0, 0.0, 0.0],
                    },
                    {
                        "offer_id": "offer-2",
                        "title": "Java Engineer",
                        "company": "Beta",
                        "description": "Backend Java",
                        "vector": [0.0, 1.0, 0.0, 0.0],
                    },
                ]
            },
        )
        assert import_response.status_code == 201

        profile_response = client.post(
            "/integration/profiles/import-vector",
            headers={"x-internal-api-key": "ingest-secret"},
            json={
                "user_id": str(user_id),
                "vector": [0.9, 0.1, 0.0, 0.0],
            },
        )
        assert profile_response.status_code == 201

        recommended_response = client.get(
            "/integration/offers/recommended",
            headers=auth_headers(user_id),
        )

    assert recommended_response.status_code == 200
    assert recommended_response.json()["total"] == 2
    assert recommended_response.json()["offers"][0]["offer_id"] == "offer-1"


def test_import_rejects_invalid_vector_size() -> None:
    """Offer import should reject vectors with wrong dimensions."""

    with build_client() as client:
        response = client.post(
            "/integration/offers/import",
            headers={"x-internal-api-key": "ingest-secret"},
            json={
                "offers": [
                    {
                        "offer_id": "offer-1",
                        "title": "Backend Developer",
                        "company": "Acme",
                        "description": "Python role",
                        "vector": [1.0, 0.0],
                    }
                ]
            },
        )

    assert response.status_code == 400
    assert "4 dimensiones" in response.json()["detail"]


def test_import_rejects_non_finite_vector_values() -> None:
    """Offer import should reject vectors containing NaN/inf values."""

    with build_client() as client:
        response = client.post(
            "/integration/offers/import",
            headers={"x-internal-api-key": "ingest-secret"},
            json={
                "offers": [
                    {
                        "offer_id": "offer-nan",
                        "title": "Backend Developer",
                        "company": "Acme",
                        "description": "Python role",
                        "vector": [1.0, "nan", 0.0, 0.0],
                    }
                ]
            },
        )

    assert response.status_code == 400
    assert "no finitos" in response.json()["detail"]
