"""MinIO storage implementation for profile artifacts."""

from datetime import datetime, timezone
from io import BytesIO
import json
from typing import Any, Protocol
from uuid import UUID

from minio import Minio
from minio.error import S3Error


class StorageBackendError(Exception):
    """Raised when an object storage operation fails."""


class ProfileStorageProtocol(Protocol):
    """Storage contract used by the profile service."""

    def store_profile_json(self, user_id: UUID, payload: dict[str, Any]) -> str:
        """Persist a profile payload and return the object key."""


class MinioProfileStorage:
    """MinIO implementation used to store extracted CV payloads."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ) -> None:
        self._bucket_name = bucket_name
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket_checked = False

    def _ensure_bucket_exists(self) -> None:
        """Create the bucket lazily if it does not exist yet."""

        if self._bucket_checked:
            return

        try:
            if not self._client.bucket_exists(self._bucket_name):
                self._client.make_bucket(self._bucket_name)
        except S3Error as exc:
            raise StorageBackendError("No se pudo preparar el bucket de perfiles") from exc

        self._bucket_checked = True

    def store_profile_json(self, user_id: UUID, payload: dict[str, Any]) -> str:
        """Store profile metadata as JSON and return the generated object key."""

        self._ensure_bucket_exists()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        object_key = f"profiles/{user_id}/cv_{timestamp}.json"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        try:
            self._client.put_object(
                self._bucket_name,
                object_key,
                BytesIO(body),
                len(body),
                content_type="application/json",
            )
        except S3Error as exc:
            raise StorageBackendError("No se pudo guardar el JSON en MinIO") from exc

        return object_key
