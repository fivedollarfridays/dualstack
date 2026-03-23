"""Tests for S3/R2 storage service — presigned URL generation."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import StorageError


class TestGenerateUploadUrl:
    def test_returns_presigned_url_string(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://bucket.s3.amazonaws.com/key?signed=1"
        )

        svc = StorageService(client=mock_client, bucket="test-bucket")
        url = svc.generate_upload_url("uploads/file.png", "image/png")

        assert url == "https://bucket.s3.amazonaws.com/key?signed=1"
        mock_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={
                "Bucket": "test-bucket",
                "Key": "uploads/file.png",
                "ContentType": "image/png",
            },
            ExpiresIn=3600,
        )

    def test_custom_expiry(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://example.com/signed"

        svc = StorageService(client=mock_client, bucket="b")
        svc.generate_upload_url("k", "text/plain", expires_in=600)

        mock_client.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={"Bucket": "b", "Key": "k", "ContentType": "text/plain"},
            ExpiresIn=600,
        )

    def test_raises_storage_error_on_client_failure(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.generate_presigned_url.side_effect = Exception("AWS error")

        svc = StorageService(client=mock_client, bucket="b")
        with pytest.raises(StorageError):
            svc.generate_upload_url("k", "image/png")


class TestGenerateDownloadUrl:
    def test_returns_presigned_get_url(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://bucket.s3.amazonaws.com/key?get=1"
        )

        svc = StorageService(client=mock_client, bucket="test-bucket")
        url = svc.generate_download_url("uploads/file.png")

        assert url == "https://bucket.s3.amazonaws.com/key?get=1"
        mock_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "test-bucket", "Key": "uploads/file.png"},
            ExpiresIn=3600,
        )

    def test_raises_storage_error_on_client_failure(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.generate_presigned_url.side_effect = Exception("timeout")

        svc = StorageService(client=mock_client, bucket="b")
        with pytest.raises(StorageError):
            svc.generate_download_url("k")


class TestDeleteObject:
    def test_deletes_object_from_bucket(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        svc = StorageService(client=mock_client, bucket="test-bucket")
        svc.delete_object("uploads/file.png")

        mock_client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="uploads/file.png",
        )

    def test_raises_storage_error_on_failure(self):
        from app.core.storage import StorageService

        mock_client = MagicMock()
        mock_client.delete_object.side_effect = Exception("access denied")

        svc = StorageService(client=mock_client, bucket="b")
        with pytest.raises(StorageError):
            svc.delete_object("k")


class TestGetStorageService:
    def setup_method(self):
        from app.core.storage import reset_storage_service

        reset_storage_service()

    def teardown_method(self):
        from app.core.storage import reset_storage_service

        reset_storage_service()

    @patch("app.core.storage.get_settings")
    @patch("app.core.storage.boto3")
    def test_creates_service_with_configured_settings(self, mock_boto3, mock_settings):
        from app.core.storage import get_storage_service

        settings = MagicMock()
        settings.storage_endpoint = "https://r2.example.com"
        settings.storage_access_key = "key123"
        settings.storage_secret_key = "secret456"
        settings.storage_bucket = "my-bucket"
        settings.storage_region = "auto"
        mock_settings.return_value = settings

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        svc = get_storage_service()

        mock_boto3.client.assert_called_once_with(
            "s3",
            endpoint_url="https://r2.example.com",
            aws_access_key_id="key123",
            aws_secret_access_key="secret456",
            region_name="auto",
        )
        assert svc.bucket == "my-bucket"

    @patch("app.core.storage.get_settings")
    def test_raises_when_not_configured(self, mock_settings):
        from app.core.storage import get_storage_service

        settings = MagicMock()
        settings.storage_bucket = ""
        settings.storage_access_key = ""
        mock_settings.return_value = settings

        with pytest.raises(StorageError, match="not configured"):
            get_storage_service()

    @patch("app.core.storage.get_settings")
    def test_raises_when_secret_key_empty(self, mock_settings):
        from app.core.storage import get_storage_service

        settings = MagicMock()
        settings.storage_bucket = "my-bucket"
        settings.storage_access_key = "key123"
        settings.storage_secret_key = ""
        mock_settings.return_value = settings

        with pytest.raises(StorageError, match="not configured"):
            get_storage_service()
