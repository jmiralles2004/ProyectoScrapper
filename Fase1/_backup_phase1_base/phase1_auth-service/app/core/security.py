"""Password and token helpers for the auth service."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import Settings


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the given password."""

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Check whether the password matches the stored hash."""

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(subject: str, settings: Settings) -> str:
    """Create a signed JWT access token for the given subject."""

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> str:
    """Decode a JWT access token and return its subject."""

    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise jwt.InvalidTokenError("Token inválido")
    return subject
