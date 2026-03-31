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


class InvalidCareerGoalError(ProfileError):
    """Raised when career transition form data is incomplete or invalid."""


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
            desired_role=profile.desired_role,
            transition_summary=profile.transition_summary,
            extracted_text_length=len(profile.cv_text),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @staticmethod
    def _clean_optional_text(value: str | None) -> str | None:
        """Normalize free text values while preserving a None sentinel."""

        if value is None:
            return None
        normalized = " ".join(value.split()).strip()
        return normalized or None

    @classmethod
    def _normalize_career_goal(
        cls,
        desired_role: str | None,
        transition_summary: str | None,
        *,
        require_complete: bool,
    ) -> tuple[str | None, str | None]:
        """Normalize and validate optional/required career transition fields."""

        normalized_role = cls._clean_optional_text(desired_role)
        normalized_summary = cls._clean_optional_text(transition_summary)

        if normalized_role is None and normalized_summary is None:
            if require_complete:
                raise InvalidCareerGoalError("Debes completar desired_role y transition_summary")
            return None, None

        if normalized_role is None or normalized_summary is None:
            raise InvalidCareerGoalError(
                "Debes indicar desired_role y transition_summary juntos"
            )

        if not 2 <= len(normalized_role) <= 120:
            raise InvalidCareerGoalError("desired_role debe tener entre 2 y 120 caracteres")

        if not 10 <= len(normalized_summary) <= 2000:
            raise InvalidCareerGoalError("transition_summary debe tener entre 10 y 2000 caracteres")

        return normalized_role, normalized_summary

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
            desired_role=profile.desired_role,
            transition_summary=profile.transition_summary,
            extracted_text_length=len(profile.cv_text),
            cv_text_preview=self._build_preview(profile.cv_text),
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def upload_cv(
        self,
        user_id: UUID,
        uploaded_file: UploadFile,
        desired_role: str | None = None,
        transition_summary: str | None = None,
    ) -> ProfileUploadResponse:
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

        existing_profile = await self._repository.get_by_user_id(user_id)
        provided_role, provided_summary = self._normalize_career_goal(
            desired_role=desired_role,
            transition_summary=transition_summary,
            require_complete=False,
        )
        resolved_role = provided_role or (existing_profile.desired_role if existing_profile is not None else None)
        resolved_summary = provided_summary or (
            existing_profile.transition_summary if existing_profile is not None else None
        )

        normalized_text = normalize_cv_text(extracted_text)
        uploaded_at = datetime.now(timezone.utc)

        payload = build_profile_etl_payload(
            user_id=user_id,
            cv_filename=filename,
            raw_text=extracted_text,
            normalized_text=normalized_text,
            extraction_method=extraction_method,
            uploaded_at=uploaded_at,
            desired_role=resolved_role,
            transition_summary=resolved_summary,
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
            desired_role=resolved_role,
            transition_summary=resolved_summary,
        )

        return self._to_upload_response(profile)

    async def get_current_profile(self, user_id: UUID) -> ProfileReadResponse:
        """Return the current profile for the authenticated user."""

        profile = await self._repository.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError("Aun no has subido un CV")
        return self._to_read_response(profile)

    async def upsert_career_goal(
        self,
        user_id: UUID,
        desired_role: str,
        transition_summary: str,
    ) -> ProfileReadResponse:
        """Store career transition intent for an already uploaded profile."""

        normalized_role, normalized_summary = self._normalize_career_goal(
            desired_role=desired_role,
            transition_summary=transition_summary,
            require_complete=True,
        )

        if normalized_role is None or normalized_summary is None:
            raise InvalidCareerGoalError("Debes completar desired_role y transition_summary")

        profile = await self._repository.update_career_goal(
            user_id=user_id,
            desired_role=normalized_role,
            transition_summary=normalized_summary,
        )
        if profile is None:
            raise ProfileNotFoundError("Aun no has subido un CV")

        return self._to_read_response(profile)
