"""Unit tests for the auth service."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.models import UserRecord
from app.services.auth import AuthService


class FakeUserRepository:
    """In-memory user repository used for tests."""

    def __init__(self) -> None:
        self._users_by_email: dict[str, UserRecord] = {}
        self._users_by_id: dict[str, UserRecord] = {}

    async def get_by_email(self, email: str) -> UserRecord | None:
        return self._users_by_email.get(email)

    async def get_by_id(self, user_id):
        return self._users_by_id.get(str(user_id))

    async def create_user(self, email: str, hashed_password: str) -> UserRecord:
        now = datetime.now(timezone.utc)
        user = UserRecord(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._users_by_email[email] = user
        self._users_by_id[str(user.id)] = user
        return user

    async def close(self) -> None:
        return None


def build_client() -> TestClient:
    """Create a test client wired to the fake repository."""

    settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/jobmatch",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        service_name="auth-service",
    )
    app = create_app(settings)
    repository = FakeUserRepository()
    app.state.user_repository = repository
    app.state.auth_service = AuthService(repository, settings)
    return TestClient(app)


def test_healthcheck_returns_service_name() -> None:
    """The health endpoint should confirm the service is running."""

    with build_client() as client:
        response = client.get("/health")
        routed_response = client.get("/auth/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "auth-service"}
    assert routed_response.status_code == 200
    assert routed_response.json() == {"status": "ok", "service": "auth-service"}


def test_register_login_and_me_flow() -> None:
    """A user can register, log in and fetch the authenticated profile."""

    with build_client() as client:
        register_response = client.post(
            "/auth/register",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        assert register_response.status_code == 201
        assert register_response.json()["email"] == "alice@example.com"
        assert "hashed_password" not in register_response.json()

        login_response = client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"


def test_duplicate_registration_returns_conflict() -> None:
    """Registering the same email twice should fail with 409."""

    with build_client() as client:
        first_response = client.post(
            "/auth/register",
            json={"email": "bob@example.com", "password": "secret123"},
        )
        assert first_response.status_code == 201

        duplicate_response = client.post(
            "/auth/register",
            json={"email": "bob@example.com", "password": "secret123"},
        )

    assert duplicate_response.status_code == 409


def test_invalid_login_returns_unauthorized() -> None:
    """Wrong credentials should return HTTP 401."""

    with build_client() as client:
        client.post(
            "/auth/register",
            json={"email": "carol@example.com", "password": "secret123"},
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "carol@example.com", "password": "wrongpass"},
        )

    assert login_response.status_code == 401
