"""FastAPI entrypoint for the Phase 1 auth service."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status

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

    app = FastAPI(title="JobMatch Auth Service", version="1.0.0", lifespan=lifespan)
    app.state.settings = resolved_settings

    @app.get("/health", response_model=HealthResponse)
    @app.get("/auth/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Return a basic healthcheck payload."""

        return HealthResponse(status="ok", service=resolved_settings.service_name)

    @app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
    async def register(
        payload: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> UserRead:
        """Register a new user."""

        try:
            return await auth_service.register(payload.email, payload.password)
        except EmailAlreadyRegisteredError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    @app.post("/auth/login", response_model=TokenResponse)
    async def login(
        payload: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ) -> TokenResponse:
        """Authenticate a user and return a JWT token."""

        try:
            return await auth_service.login(payload.email, payload.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @app.get("/auth/me", response_model=UserRead)
    async def me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
        """Return the authenticated user profile."""

        return current_user

    return app
