"""Business logic for authentication workflows."""

from uuid import UUID

import jwt

from ..core.config import Settings
from ..core.security import create_access_token, decode_access_token, hash_password, verify_password
from ..models import UserRecord
from ..repositories.users import UserRepositoryProtocol
from ..schemas import TokenResponse, UserRead


class AuthError(Exception):
    """Base class for auth service errors."""


class EmailAlreadyRegisteredError(AuthError):
    """Raised when trying to register an existing email."""


class InvalidCredentialsError(AuthError):
    """Raised when the provided credentials are invalid."""


class InvalidTokenError(AuthError):
    """Raised when the bearer token cannot be decoded."""


class UserNotFoundError(AuthError):
    """Raised when the token points to a missing user."""


class AuthService:
    """Application service that coordinates auth operations."""

    def __init__(self, repository: UserRepositoryProtocol, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    @staticmethod
    def _normalize_email(email: str) -> str:
        """Normalize email addresses before persistence and lookup."""

        return email.strip().lower()

    def _to_public_user(self, user: UserRecord) -> UserRead:
        """Convert a stored user into a public response model."""

        return UserRead.model_validate(user)

    async def register(self, email: str, password: str) -> UserRead:
        """Register a new user."""

        normalized_email = self._normalize_email(email)
        existing_user = await self._repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise EmailAlreadyRegisteredError("El email ya está registrado")

        hashed_password = hash_password(password)
        created_user = await self._repository.create_user(normalized_email, hashed_password)
        return self._to_public_user(created_user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return a JWT access token."""

        normalized_email = self._normalize_email(email)
        user = await self._repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Credenciales inválidas")

        access_token = create_access_token(str(user.id), self._settings)
        return TokenResponse(access_token=access_token)

    async def get_current_user(self, token: str) -> UserRead:
        """Return the authenticated user associated with a token."""

        try:
            subject = decode_access_token(token, self._settings)
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("Token inválido o expirado") from exc

        try:
            user_id = UUID(subject)
        except ValueError as exc:
            raise InvalidTokenError("Token inválido") from exc

        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("Usuario no encontrado")

        return self._to_public_user(user)
