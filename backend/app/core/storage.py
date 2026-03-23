"""S3/R2-compatible object storage service with presigned URL generation."""

import logging

import boto3

from app.core.config import get_settings
from app.core.errors import StorageError

logger = logging.getLogger(__name__)


class StorageService:
    """Thin wrapper around an S3 client for presigned URL operations."""

    def __init__(self, client, bucket: str):
        self._client = client
        self.bucket = bucket

    def generate_upload_url(
        self, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        try:
            return self._client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
        except Exception as exc:
            logger.exception("Upload URL generation failed for key=%s", key)
            raise StorageError(message="Upload URL generation failed") from exc

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except Exception as exc:
            logger.exception("Download URL generation failed for key=%s", key)
            raise StorageError(message="Download URL generation failed") from exc

    def delete_object(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            logger.exception("File deletion failed for key=%s", key)
            raise StorageError(message="File deletion failed") from exc


_storage_service: StorageService | None = None


def reset_storage_service() -> None:
    """Reset the cached storage service (for testing)."""
    global _storage_service
    _storage_service = None


def get_storage_service() -> StorageService:
    """Get or create a cached StorageService singleton."""
    global _storage_service
    if _storage_service is not None:
        return _storage_service

    settings = get_settings()

    if not settings.storage_bucket or not settings.storage_access_key or not settings.storage_secret_key:
        raise StorageError(message="Object storage is not configured")

    client = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
    )
    _storage_service = StorageService(client=client, bucket=settings.storage_bucket)
    return _storage_service
