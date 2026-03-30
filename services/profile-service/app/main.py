"""FastAPI entrypoint for the Phase 2 profile service."""

from contextlib import asynccontextmanager
from functools import partial

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status

from .core.config import Settings, get_settings
from .dependencies import get_current_user_id, get_profile_service
from .repositories.profiles import PostgresProfileRepository
from .schemas import HealthResponse, ProfileReadResponse, ProfileUploadResponse
from .services.profiles import (
    EmptyPdfError,
    InvalidPdfError,
    ProfileNotFoundError,
    ProfileService,
    StorageError,
)
from .storage.minio_storage import MinioProfileStorage
from .utils.pdf import extract_text_from_pdf


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the profile service application."""

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        """Prepare and tear down application resources."""

        if not hasattr(application.state, "profile_repository"):
            application.state.profile_repository = PostgresProfileRepository(resolved_settings.database_url)

        if not hasattr(application.state, "profile_storage"):
            application.state.profile_storage = MinioProfileStorage(
                endpoint=resolved_settings.minio_endpoint,
                access_key=resolved_settings.minio_root_user,
                secret_key=resolved_settings.minio_root_password,
                bucket_name=resolved_settings.minio_bucket_profiles,
                secure=resolved_settings.minio_secure,
            )

        if not hasattr(application.state, "profile_service"):
            cv_text_extractor = partial(
                extract_text_from_pdf,
                ocr_enabled=resolved_settings.ocr_enabled,
                ocr_languages=resolved_settings.ocr_languages,
                ocr_dpi=resolved_settings.ocr_dpi,
            )
            application.state.profile_service = ProfileService(
                repository=application.state.profile_repository,
                storage=application.state.profile_storage,
                cv_text_extractor=cv_text_extractor,
                storage_bucket=resolved_settings.minio_bucket_profiles,
            )

        yield

        repository = getattr(application.state, "profile_repository", None)
        if repository is not None:
            await repository.close()

    app = FastAPI(title="JobMatch Profile Service", version="1.0.0", lifespan=lifespan)
    app.state.settings = resolved_settings

    @app.get("/health", response_model=HealthResponse)
    @app.get("/profiles/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Return a basic healthcheck payload."""

        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.post("/profiles/cv", response_model=ProfileUploadResponse, status_code=status.HTTP_201_CREATED)
    async def upload_cv(
        file: UploadFile = File(...),
        user_id=Depends(get_current_user_id),
        profile_service: ProfileService = Depends(get_profile_service),
    ) -> ProfileUploadResponse:
        """Upload a CV PDF for the authenticated user."""

        try:
            return await profile_service.upload_cv(user_id, file)
        except InvalidPdfError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except EmptyPdfError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except StorageError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    @app.get("/profiles/me", response_model=ProfileReadResponse)
    async def get_profile(
        user_id=Depends(get_current_user_id),
        profile_service: ProfileService = Depends(get_profile_service),
    ) -> ProfileReadResponse:
        """Return the profile associated with the authenticated user."""

        try:
            return await profile_service.get_current_profile(user_id)
        except ProfileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return app
