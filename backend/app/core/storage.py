"""S3/R2-compatible object storage service with presigned URL generation."""

import boto3

from app.core.config import get_settings
from app.core.errors import StorageError


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
            raise StorageError(message=f"Failed to generate upload URL: {exc}") from exc

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except Exception as exc:
            raise StorageError(
                message=f"Failed to generate download URL: {exc}"
            ) from exc

    def delete_object(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            raise StorageError(message=f"Failed to delete object: {exc}") from exc


def get_storage_service() -> StorageService:
    """Create a StorageService from environment settings."""
    settings = get_settings()

    if not settings.storage_bucket or not settings.storage_access_key:
        raise StorageError(message="Object storage is not configured")

    client = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
    )
    return StorageService(client=client, bucket=settings.storage_bucket)
