"""Tests for file upload schema validation — content_type allowlist."""

import pytest
from pydantic import ValidationError

from app.files.schemas import UploadUrlRequest, UploadUrlResponse


class TestContentTypeAllowlist:
    """Validate that only safe MIME types are accepted."""

    def test_accepts_image_png(self):
        req = UploadUrlRequest(filename="a.png", content_type="image/png", size=100)
        assert req.content_type == "image/png"

    def test_accepts_image_jpeg(self):
        req = UploadUrlRequest(filename="a.jpg", content_type="image/jpeg", size=100)
        assert req.content_type == "image/jpeg"

    def test_accepts_application_pdf(self):
        req = UploadUrlRequest(
            filename="a.pdf", content_type="application/pdf", size=100
        )
        assert req.content_type == "application/pdf"

    def test_accepts_text_plain(self):
        req = UploadUrlRequest(filename="a.txt", content_type="text/plain", size=100)
        assert req.content_type == "text/plain"

    def test_accepts_text_csv(self):
        req = UploadUrlRequest(filename="a.csv", content_type="text/csv", size=100)
        assert req.content_type == "text/csv"

    def test_accepts_application_json(self):
        req = UploadUrlRequest(
            filename="a.json", content_type="application/json", size=100
        )
        assert req.content_type == "application/json"

    def test_accepts_image_gif(self):
        req = UploadUrlRequest(filename="a.gif", content_type="image/gif", size=100)
        assert req.content_type == "image/gif"

    def test_accepts_image_webp(self):
        req = UploadUrlRequest(filename="a.webp", content_type="image/webp", size=100)
        assert req.content_type == "image/webp"

    def test_rejects_text_html(self):
        with pytest.raises(ValidationError, match="not allowed"):
            UploadUrlRequest(filename="a.html", content_type="text/html", size=100)

    def test_rejects_image_svg_xml(self):
        with pytest.raises(ValidationError, match="not allowed"):
            UploadUrlRequest(filename="a.svg", content_type="image/svg+xml", size=100)

    def test_rejects_application_octet_stream(self):
        with pytest.raises(ValidationError, match="not allowed"):
            UploadUrlRequest(
                filename="a.bin", content_type="application/octet-stream", size=100
            )

    def test_rejects_application_javascript(self):
        with pytest.raises(ValidationError, match="not allowed"):
            UploadUrlRequest(
                filename="a.js", content_type="application/javascript", size=100
            )

    def test_rejects_text_xml(self):
        with pytest.raises(ValidationError, match="not allowed"):
            UploadUrlRequest(filename="a.xml", content_type="text/xml", size=100)


class TestUploadUrlResponseNoStorageKey:
    """UploadUrlResponse must NOT expose storage_key."""

    def test_response_has_no_storage_key_field(self):
        """storage_key should not be in the model fields."""
        assert "storage_key" not in UploadUrlResponse.model_fields

    def test_response_construction_without_storage_key(self):
        resp = UploadUrlResponse(
            file_id="abc", upload_url="https://s3.example.com/signed"
        )
        assert resp.file_id == "abc"
        assert resp.upload_url == "https://s3.example.com/signed"
        assert not hasattr(resp, "storage_key")

    def test_response_ignores_extra_storage_key(self):
        """Passing storage_key as extra should not include it in output."""
        resp = UploadUrlResponse(
            file_id="abc",
            upload_url="https://s3.example.com/signed",
            storage_key="uploads/user-1/abc/file.png",  # type: ignore[call-arg]
        )
        data = resp.model_dump()
        assert "storage_key" not in data
