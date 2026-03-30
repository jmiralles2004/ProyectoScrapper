"""FastAPI dependencies for the integration service."""

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .core.config import Settings
from .core.security import decode_user_id_from_token
from .services.integration import IntegrationService

bearer_scheme = HTTPBearer(auto_error=False)


def get_integration_service(request: Request) -> IntegrationService:
    """Fetch the shared integration service from application state."""

    return request.app.state.integration_service


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


async def verify_ingest_api_key(
    request: Request,
    settings: Settings = Depends(get_settings_from_request),
) -> None:
    """Validate internal API key for ingestion endpoints when configured."""

    expected_key = settings.integration_ingest_api_key.strip()
    if not expected_key:
        return

    provided_key = (request.headers.get("x-internal-api-key") or "").strip()
    if provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )
