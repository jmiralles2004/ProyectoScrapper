"""Business logic for profile and CV workflows."""

from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

from fastapi import UploadFile

from ..models import ProfileRecord
from ..repositories.profiles import ProfileRepositoryProtocol
from ..schemas import ProfileReadResponse, ProfileUploadResponse
from ..storage.minio_storage import ProfileStorageProtocol, StorageBackendError
from ..utils.cv_etl import build_profile_etl_payload, normalize_cv_text
from ..utils.pdf import PdfExtractionError, PdfTextExtractionResult, extract_text_from_pdf


class ProfileError(Exception):
    """Base class for profile service errors."""


class InvalidPdfError(ProfileError):
    """Raised when the uploaded file is not a valid PDF."""


class EmptyPdfError(ProfileError):
    """Raised when a PDF has no extractable text."""


class StorageError(ProfileError):
    """Raised when profile data cannot be stored."""


class ProfileNotFoundError(ProfileError):
    """Raised when the user profile does not exist."""


class ProfileService:
    """Application service that coordinates profile operations."""

    def __init__(
        self,
        repository: ProfileRepositoryProtocol,
        storage: ProfileStorageProtocol,
        cv_text_extractor: Callable[[bytes], str | PdfTextExtractionResult] = extract_text_from_pdf,
        storage_bucket: str = "profiles",
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._extract_text = cv_text_extractor
        self._storage_bucket = storage_bucket

    @staticmethod
    def _to_upload_response(profile: ProfileRecord) -> ProfileUploadResponse:
        """Convert a profile record into the upload response model."""

        return ProfileUploadResponse(
            id=profile.id,
            user_id=profile.user_id,
            cv_filename=profile.cv_filename,
            cv_object_key=profile.cv_object_key,
            storage_bucket=profile.storage_bucket,
            extracted_text_length=len(profile.cv_text),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @staticmethod
    def _build_preview(cv_text: str, max_chars: int = 280) -> str:
        """Build a compact preview from the extracted CV text."""

        compact_text = cv_text.replace("\n", " ").strip()
        if len(compact_text) <= max_chars:
            return compact_text
        return compact_text[: max_chars - 3].rstrip() + "..."

    def _to_read_response(self, profile: ProfileRecord) -> ProfileReadResponse:
        """Convert a profile record into the read response model."""

        return ProfileReadResponse(
            id=profile.id,
            user_id=profile.user_id,
            cv_filename=profile.cv_filename,
            cv_object_key=profile.cv_object_key,
            storage_bucket=profile.storage_bucket,
            extracted_text_length=len(profile.cv_text),
            cv_text_preview=self._build_preview(profile.cv_text),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def upload_cv(self, user_id: UUID, uploaded_file: UploadFile) -> ProfileUploadResponse:
        """Validate, extract and store a CV PDF for a user."""

        filename = (uploaded_file.filename or "").strip()
        if not filename.lower().endswith(".pdf"):
            raise InvalidPdfError("Solo se permiten archivos PDF")

        file_bytes = await uploaded_file.read()
        if not file_bytes:
            raise InvalidPdfError("El archivo PDF esta vacio")

        try:
            extraction_output = self._extract_text(file_bytes)
        except PdfExtractionError as exc:
            raise InvalidPdfError("No se pudo extraer texto del PDF") from exc

        extraction_method = "unknown"
        if isinstance(extraction_output, PdfTextExtractionResult):
            extracted_text = extraction_output.text.strip()
            extraction_method = extraction_output.method
        else:
            extracted_text = str(extraction_output).strip()

        if not extracted_text:
            raise EmptyPdfError("No se pudo extraer texto del PDF ni con OCR")

        normalized_text = normalize_cv_text(extracted_text)
        uploaded_at = datetime.now(timezone.utc)

        payload = build_profile_etl_payload(
            user_id=user_id,
            cv_filename=filename,
            raw_text=extracted_text,
            normalized_text=normalized_text,
            extraction_method=extraction_method,
            uploaded_at=uploaded_at,
        )

        try:
            object_key = self._storage.store_profile_json(user_id, payload)
        except StorageBackendError as exc:
            raise StorageError("No se pudo guardar el perfil en MinIO") from exc

        profile = await self._repository.upsert_profile(
            user_id=user_id,
            cv_filename=filename,
            cv_text=normalized_text,
            cv_object_key=object_key,
            storage_bucket=self._storage_bucket,
        )

        return self._to_upload_response(profile)

    async def get_current_profile(self, user_id: UUID) -> ProfileReadResponse:
        """Return the current profile for the authenticated user."""

        profile = await self._repository.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError("Aun no has subido un CV")
        return self._to_read_response(profile)
