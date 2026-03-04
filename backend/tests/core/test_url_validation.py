"""Tests for URL validation utilities."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.url_validation import validate_redirect_url
from tests.helpers import mock_settings_with_cors


class TestValidateRedirectUrl:
    @patch("app.core.url_validation.get_settings")
    def test_allows_configured_origin(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        result = validate_redirect_url("https://example.com/dashboard?checkout=success")
        assert result == "https://example.com/dashboard?checkout=success"

    @patch("app.core.url_validation.get_settings")
    def test_rejects_foreign_origin(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="URL origin is not allowed"):
            validate_redirect_url("https://evil.com/phish")

    @patch("app.core.url_validation.get_settings")
    def test_rejects_no_scheme(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Only http and https URLs are allowed"):
            validate_redirect_url("example.com/dashboard")

    @patch("app.core.url_validation.get_settings")
    def test_rejects_javascript_scheme(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Only http and https URLs are allowed"):
            validate_redirect_url("javascript:alert(1)")

    @patch("app.core.url_validation.get_settings")
    def test_rejects_data_scheme(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Only http and https URLs are allowed"):
            validate_redirect_url("data:text/html,test")

    @patch("app.core.url_validation.get_settings")
    def test_rejects_ftp_scheme(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Only http and https URLs are allowed"):
            validate_redirect_url("ftp://example.com/file")

    @patch("app.core.url_validation.get_settings")
    def test_rejects_empty_netloc(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="URL must have a valid host"):
            validate_redirect_url("http://")

    @patch("app.core.url_validation.get_settings")
    def test_allows_localhost_in_dev(self, mock_get_settings: MagicMock) -> None:
        mock_get_settings.return_value = mock_settings_with_cors("http://localhost:3000")
        result = validate_redirect_url("http://localhost:3000/dashboard")
        assert result == "http://localhost:3000/dashboard"
