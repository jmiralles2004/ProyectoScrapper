"""FastAPI entrypoint for the Phase 1 auth service."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html

from .core.config import Settings, get_settings
from .dependencies import get_auth_service, get_current_user
from .repositories.users import PostgresUserRepository
from .schemas import HealthResponse, LoginRequest, RegisterRequest, TokenResponse, UserRead
from .services.auth import AuthService, EmailAlreadyRegisteredError, InvalidCredentialsError


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the auth service application."""

    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        """Prepare and tear down application resources."""

        if not hasattr(application.state, "user_repository"):
            application.state.user_repository = PostgresUserRepository(resolved_settings.database_url)
        if not hasattr(application.state, "auth_service"):
            application.state.auth_service = AuthService(application.state.user_repository, resolved_settings)

        yield

        repository = getattr(application.state, "user_repository", None)
        if repository is not None:
            await repository.close()

    app = FastAPI(
        title="JobMatch Auth Service",
        version="1.0.0",
        lifespan=lifespan,
        description=(
            "Servicio de autenticacion e identidad para JobMatch.\n\n"
            "Flujo recomendado:\n"
            "1. Registrar usuario con `/auth/register`.\n"
            "2. Iniciar sesion con `/auth/login` para obtener JWT.\n"
            "3. Enviar `Authorization: Bearer <token>` para `/auth/me`."
        ),
    )
    app.state.settings = resolved_settings

    health_description = (
        "Verifica que el servicio esta activo y responde.\n\n"
        "- No requiere autenticacion.\n"
        "- Lo usan Docker, Nginx y monitoreo para readiness/liveness.\n"
        "- Devuelve `status` y `service`."
    )

    register_description = (
        "Crea una cuenta nueva en la base de datos.\n\n"
        "- Recibe `email` y `password`.\n"
        "- El email se normaliza y no puede repetirse.\n"
        "- Devuelve el usuario creado sin exponer la contrasena."
    )

    login_description = (
        "Autentica un usuario y devuelve un token JWT de acceso.\n\n"
        "- El token se envia luego en `Authorization: Bearer <token>`.\n"
        "- Si email o password no coinciden, devuelve 401."
    )

    me_description = (
        "Devuelve los datos publicos del usuario autenticado.\n\n"
        "- Requiere token Bearer valido.\n"
        "- No devuelve informacion sensible (por ejemplo, hash de password)."
    )

    @app.get(
        "/health",
        response_model=HealthResponse,
        summary="Verificar estado del auth-service",
        description=health_description,
        tags=["Health"],
    )
    @app.get(
        "/auth/health",
        response_model=HealthResponse,
        summary="Verificar estado del auth-service (prefijo auth)",
        description=health_description,
        tags=["Health"],
    )
    async def health() -> HealthResponse:
        """Return a basic healthcheck payload."""

        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.post(
        "/auth/register",
        response_model=UserRead,
        status_code=status.HTTP_201_CREATED,
        summary="Registrar un usuario nuevo",
        description=register_description,
        responses={
            409: {"description": "El email ya esta registrado"},
            422: {"description": "Datos de entrada invalidos"},
        },
        tags=["Auth"],
    )
    async def register(
        payload: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> UserRead:
        """Register a new user."""

        try:
            return await auth_service.register(payload.email, payload.password)
        except EmailAlreadyRegisteredError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    @app.post(
        "/auth/login",
        response_model=TokenResponse,
        summary="Iniciar sesion y obtener JWT",
        description=login_description,
        responses={
            401: {"description": "Credenciales invalidas"},
            422: {"description": "Datos de entrada invalidos"},
        },
        tags=["Auth"],
    )
    async def login(
        payload: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> TokenResponse:
        """Authenticate a user and return a JWT token."""

        try:
            return await auth_service.login(payload.email, payload.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @app.get(
        "/auth/me",
        response_model=UserRead,
        summary="Consultar usuario autenticado",
        description=me_description,
        responses={
            401: {"description": "Falta token o token invalido/expirado"},
        },
        tags=["Auth"],
    )
    async def me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
        """Return the authenticated user profile."""

        return current_user

    @app.get("/auth/openapi.json", include_in_schema=False)
    async def auth_openapi() -> dict[str, Any]:
        """Expose OpenAPI schema through the /auth prefix for gateway usage."""

        return app.openapi()

    @app.get("/auth/docs", include_in_schema=False)
    async def auth_docs():
        """Expose Swagger UI through the /auth prefix for gateway usage."""

        return get_swagger_ui_html(
            openapi_url="/auth/openapi.json",
            title=f"{app.title} - Swagger UI",
        )

    return app
