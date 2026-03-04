"""Tests for app.core.config module."""

from app.core.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_get_settings_returns_settings_instance(self):
        """get_settings should return a Settings instance."""
        result = get_settings()
        assert isinstance(result, Settings)

    def test_default_environment(self):
        """Default environment should be 'development'."""
        settings = Settings()
        assert settings.environment == "development"

    def test_default_log_level(self):
        """Default log level should be 'INFO'."""
        settings = Settings()
        assert settings.log_level == "INFO"

    def test_default_cors_origins(self):
        """Default CORS origins should be localhost:3000."""
        settings = Settings()
        assert settings.cors_origins == "http://localhost:3000"

    def test_get_cors_origins_single_origin(self):
        """get_cors_origins with a single origin should return list with one item."""
        settings = Settings(cors_origins="http://localhost:3000")
        result = settings.get_cors_origins()
        assert result == ["http://localhost:3000"]

    def test_get_cors_origins_multiple_origins(self):
        """get_cors_origins with comma-separated string should return list."""
        settings = Settings(
            cors_origins="http://localhost:3000,https://example.com,https://app.example.com"
        )
        result = settings.get_cors_origins()
        assert result == [
            "http://localhost:3000",
            "https://example.com",
            "https://app.example.com",
        ]

    def test_get_cors_origins_with_whitespace(self):
        """get_cors_origins should strip whitespace around origins."""
        settings = Settings(cors_origins="  http://a.com , http://b.com  ")
        result = settings.get_cors_origins()
        assert result == ["http://a.com", "http://b.com"]

    def test_get_cors_origins_ignores_empty_entries(self):
        """get_cors_origins should skip empty entries from trailing commas."""
        settings = Settings(cors_origins="http://a.com,,http://b.com,")
        result = settings.get_cors_origins()
        assert result == ["http://a.com", "http://b.com"]

    def test_default_turso_database_url_is_empty(self):
        """Default turso_database_url should be empty string."""
        settings = Settings()
        assert settings.turso_database_url == ""
