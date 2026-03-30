"""FastAPI dependencies for the auth service."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .schemas import UserRead
from .services.auth import AuthService, InvalidTokenError, UserNotFoundError

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthService:
    """Fetch the shared auth service from application state."""

    return request.app.state.auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """Resolve the current user from the bearer token."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token Bearer",
        )

    try:
        return await auth_service.get_current_user(credentials.credentials)
    except (InvalidTokenError, UserNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
