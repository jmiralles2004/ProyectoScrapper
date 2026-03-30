"""Unit tests for the profile service."""

from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID, uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.models import ProfileRecord
from app.services.profiles import ProfileService
from app.utils.pdf import PdfTextExtractionResult


class FakeProfileRepository:
    """In-memory repository used for profile service tests."""

    def __init__(self) -> None:
        self._profiles: dict[str, ProfileRecord] = {}

    async def get_by_user_id(self, user_id: UUID) -> ProfileRecord | None:
        return self._profiles.get(str(user_id))

    async def upsert_profile(
        self,
        user_id: UUID,
        cv_filename: str,
        cv_text: str,
        cv_object_key: str,
        storage_bucket: str,
    ) -> ProfileRecord:
        existing = self._profiles.get(str(user_id))
        now = datetime.now(timezone.utc)
        created_at = existing.created_at if existing is not None else now
        profile = ProfileRecord(
            id=existing.id if existing is not None else uuid4(),
            user_id=user_id,
            cv_filename=cv_filename,
            cv_text=cv_text,
            cv_object_key=cv_object_key,
            storage_bucket=storage_bucket,
            created_at=created_at,
            updated_at=now,
        )
        self._profiles[str(user_id)] = profile
        return profile

    async def close(self) -> None:
        return None


class FakeProfileStorage:
    """In-memory storage backend used for tests."""

    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def store_profile_json(self, user_id: UUID, payload: dict) -> str:
        object_key = f"profiles/{user_id}/cv_test.json"
        self._data[object_key] = payload
        return object_key


def build_client(cv_text_extractor: Callable[[bytes], str] | None = None) -> TestClient:
    """Create a test client with fake persistence and storage."""

    extractor = cv_text_extractor or (lambda _: "Texto extraido del CV de prueba")

    settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/jobmatch",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        minio_endpoint="localhost:9000",
        minio_root_user="minioadmin",
        minio_root_password="minioadmin123",
        minio_bucket_profiles="profiles",
        minio_secure=False,
        ocr_enabled=True,
        ocr_languages="spa+eng",
        ocr_dpi=300,
        service_name="profile-service",
    )
    app = create_app(settings)
    repository = FakeProfileRepository()
    storage = FakeProfileStorage()
    app.state.profile_repository = repository
    app.state.profile_storage = storage
    app.state.profile_service = ProfileService(
        repository=repository,
        storage=storage,
        cv_text_extractor=extractor,
        storage_bucket="profiles",
    )
    return TestClient(app)


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


def test_healthcheck_returns_service_name() -> None:
    """The health endpoints should confirm the service is running."""

    with build_client() as client:
        response = client.get("/health")
        routed_response = client.get("/profiles/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "profile-service"}
    assert routed_response.status_code == 200
    assert routed_response.json() == {"status": "ok", "service": "profile-service"}


def test_upload_and_fetch_profile_flow() -> None:
    """A user can upload a CV and fetch their current profile."""

    user_id = uuid4()

    with build_client() as client:
        upload_response = client.post(
            "/profiles/cv",
            headers=auth_headers(user_id),
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert upload_response.status_code == 201
        assert upload_response.json()["user_id"] == str(user_id)
        assert upload_response.json()["storage_bucket"] == "profiles"
        assert upload_response.json()["extracted_text_length"] > 0

        me_response = client.get("/profiles/me", headers=auth_headers(user_id))

    assert me_response.status_code == 200
    assert me_response.json()["user_id"] == str(user_id)
    assert me_response.json()["cv_filename"] == "cv.pdf"
    assert "Texto extraido" in me_response.json()["cv_text_preview"]


def test_upload_requires_bearer_token() -> None:
    """Uploading a CV without a token should return HTTP 401."""

    with build_client() as client:
        response = client.post(
            "/profiles/cv",
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert response.status_code == 401


def test_upload_rejects_non_pdf_files() -> None:
    """The API should reject files that are not PDFs."""

    user_id = uuid4()

    with build_client() as client:
        response = client.post(
            "/profiles/cv",
            headers=auth_headers(user_id),
            files={"file": ("cv.txt", b"hola", "text/plain")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Solo se permiten archivos PDF"


def test_upload_returns_422_when_no_text_even_with_ocr() -> None:
    """Uploading a PDF with no extractable content should return HTTP 422."""

    user_id = uuid4()

    with build_client(cv_text_extractor=lambda _: "") as client:
        response = client.post(
            "/profiles/cv",
            headers=auth_headers(user_id),
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "No se pudo extraer texto del PDF ni con OCR"


def test_profile_me_returns_404_when_missing() -> None:
    """Requesting the profile without upload should return HTTP 404."""

    user_id = uuid4()

    with build_client() as client:
        response = client.get("/profiles/me", headers=auth_headers(user_id))

    assert response.status_code == 404


def test_upload_stores_etl_payload_structure() -> None:
    """Uploading a CV should persist ETL metadata and structured sections in storage."""

    user_id = uuid4()

    with build_client(
        cv_text_extractor=lambda _: PdfTextExtractionResult(
            text="CONTACTO\ncorreo@example.com\nEXPERIENCIA\nDevOps\nFORMACIÓN\nASIR",
            method="ocr",
        )
    ) as client:
        upload_response = client.post(
            "/profiles/cv",
            headers=auth_headers(user_id),
            files={"file": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

        assert upload_response.status_code == 201
        object_key = upload_response.json()["cv_object_key"]
        payload = client.app.state.profile_storage._data[object_key]

    assert payload["version"] == "phase2-etl-v1"
    assert payload["extraction"]["method"] == "ocr"
    assert "raw" in payload
    assert "normalized" in payload
    assert "quality" in payload
    assert payload["normalized"]["sections"]["experience"] == "DevOps"
