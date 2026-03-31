"""FastAPI entrypoint for the Phase 2 profile service."""

from contextlib import asynccontextmanager
from functools import partial
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.openapi.docs import get_swagger_ui_html

from .core.config import Settings, get_settings
from .dependencies import get_current_user_id, get_profile_service
from .repositories.profiles import PostgresProfileRepository
from .schemas import CareerGoalUpsertRequest, HealthResponse, ProfileReadResponse, ProfileUploadResponse
from .services.profiles import (
    EmptyPdfError,
    InvalidCareerGoalError,
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

        ensure_schema = getattr(application.state.profile_repository, "ensure_profile_schema", None)
        if callable(ensure_schema):
            await ensure_schema()

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

    app = FastAPI(
        title="JobMatch Profile Service",
        version="1.0.0",
        lifespan=lifespan,
        description=(
            "Gestion de CV y perfil profesional del usuario autenticado.\n\n"
            "Este servicio recibe CV en PDF, extrae/normaliza texto y guarda:\n"
            "- Metadatos en PostgreSQL\n"
            "- Documento estructurado del perfil en MinIO"
        ),
    )
    app.state.settings = resolved_settings

    health_description = (
        "Verifica que el profile-service esta activo y respondiendo.\n\n"
        "No requiere autenticacion y se usa para healthchecks de infraestructura."
    )

    upload_cv_description = (
        "Sube un CV en formato PDF para el usuario autenticado.\n\n"
        "- Requiere token Bearer.\n"
        "- Recibe `multipart/form-data` con campo `file`.\n"
        "- Puede incluir el formulario de transicion profesional con `desired_role` y `transition_summary`.\n"
        "- Extrae texto del PDF (con OCR si aplica), normaliza contenido y guarda datos de perfil.\n"
        "- Devuelve metadatos del perfil actualizado."
    )

    get_profile_description = (
        "Recupera el perfil del usuario autenticado.\n\n"
        "Incluye nombre del CV, bucket/key de almacenamiento y preview del texto extraido."
    )

    upsert_career_goal_description = (
        "Guarda el formulario de objetivo de cambio profesional del usuario autenticado.\n\n"
        "- Requiere token Bearer y que exista CV previo.\n"
        "- Permite declarar el rol objetivo y un contexto de transicion.\n"
        "- Se usa para orientar recomendaciones en escenarios de reconversion laboral."
    )

    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Verificar estado del profile-service",
        description=health_description,
        tags=["Health"],
    )
    @app.get(
        "/profiles/health",
        response_model=HealthResponse,
        summary="Verificar estado del profile-service (prefijo profiles)",
        description=health_description,
        tags=["Health"],
    )
    async def health() -> HealthResponse:
        """Return a basic healthcheck payload."""

        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.post(
        "/profiles/cv",
        response_model=ProfileUploadResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Subir CV PDF del usuario autenticado",
        description=upload_cv_description,
        responses={
            400: {"description": "El archivo no es un PDF valido"},
            401: {"description": "Falta token o token invalido/expirado"},
            422: {"description": "PDF sin texto extraible o request invalido"},
            502: {"description": "Error guardando datos en almacenamiento"},
        },
        tags=["Profiles"],
    )
    async def upload_cv(
        file: UploadFile = File(
            ...,
            description="Archivo CV en formato PDF.",
        ),
        desired_role: str | None = Form(
            default=None,
            description="Rol objetivo opcional para transicion profesional.",
        ),
        transition_summary: str | None = Form(
            default=None,
            description="Resumen opcional del cambio profesional deseado.",
        ),
        user_id=Depends(get_current_user_id),
        profile_service: ProfileService = Depends(get_profile_service),
    ) -> ProfileUploadResponse:
        """Upload a CV PDF for the authenticated user."""

        try:
            return await profile_service.upload_cv(
                user_id=user_id,
                uploaded_file=file,
                desired_role=desired_role,
                transition_summary=transition_summary,
            )
        except InvalidPdfError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except EmptyPdfError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except InvalidCareerGoalError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except StorageError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    @app.put(
        "/profiles/career-goals",
        response_model=ProfileReadResponse,
        summary="Guardar formulario de objetivo profesional",
        description=upsert_career_goal_description,
        responses={
            401: {"description": "Falta token o token invalido/expirado"},
            404: {"description": "El usuario aun no ha subido CV"},
            422: {"description": "Formulario de objetivo profesional invalido"},
        },
        tags=["Profiles"],
    )
    async def upsert_career_goal(
        payload: CareerGoalUpsertRequest,
        user_id=Depends(get_current_user_id),
        profile_service: ProfileService = Depends(get_profile_service),
    ) -> ProfileReadResponse:
        """Upsert the authenticated user's career transition form data."""

        try:
            return await profile_service.upsert_career_goal(
                user_id=user_id,
                desired_role=payload.desired_role,
                transition_summary=payload.transition_summary,
            )
        except InvalidCareerGoalError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        except ProfileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get(
        "/profiles/me",
        response_model=ProfileReadResponse,
        summary="Consultar perfil del usuario autenticado",
        description=get_profile_description,
        responses={
            401: {"description": "Falta token o token invalido/expirado"},
            404: {"description": "El usuario aun no ha subido CV"},
        },
        tags=["Profiles"],
    )
    async def get_profile(
        user_id=Depends(get_current_user_id),
        profile_service: ProfileService = Depends(get_profile_service),
    ) -> ProfileReadResponse:
        """Return the profile associated with the authenticated user."""

        try:
            return await profile_service.get_current_profile(user_id)
        except ProfileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.get("/profiles/openapi.json", include_in_schema=False)
    async def profiles_openapi() -> dict[str, Any]:
        """Expose OpenAPI schema through the /profiles prefix for gateway usage."""

        return app.openapi()

    @app.get("/profiles/docs", include_in_schema=False)
    async def profiles_docs():
        """Expose Swagger UI through the /profiles prefix for gateway usage."""

        return get_swagger_ui_html(
            openapi_url="/profiles/openapi.json",
            title=f"{app.title} - Swagger UI",
        )

    return app
