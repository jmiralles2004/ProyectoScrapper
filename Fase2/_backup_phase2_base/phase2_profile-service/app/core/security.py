"""Token helpers for the profile service."""

from uuid import UUID

import jwt

from .config import Settings


def decode_user_id_from_token(token: str, settings: Settings) -> UUID:
    """Decode a JWT and return the user identifier from its subject."""

    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise jwt.InvalidTokenError("Token invalido")

    try:
        return UUID(subject)
    except ValueError as exc:
        raise jwt.InvalidTokenError("Token invalido") from exc
