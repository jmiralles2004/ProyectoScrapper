"""FastAPI dependencies for the profile service."""

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import Settings
from .core.security import decode_user_id_from_token
from .services.profiles import ProfileService

bearer_scheme = HTTPBearer(auto_error=False)


def get_profile_service(request: Request) -> ProfileService:
    """Fetch the shared profile service from application state."""

    return request.app.state.profile_service


def get_settings_from_request(request: Request) -> Settings:
    """Fetch settings from the current application state."""

    return request.app.state.settings


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings_from_request),
) -> UUID:
    """Resolve the current user identifier from the bearer token."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token Bearer",
        )

    try:
        return decode_user_id_from_token(credentials.credentials, settings)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        ) from exc
