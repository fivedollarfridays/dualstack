"""Tests for app.core.config module."""

import pytest
from pydantic import ValidationError

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


class TestEnvironmentValidation:
    """Test that the environment field only accepts valid values."""

    def test_rejects_staging(self):
        """ENVIRONMENT=staging should raise ValidationError."""
        with pytest.raises(ValidationError, match="environment"):
            Settings(environment="staging")

    def test_rejects_prod_typo(self):
        """ENVIRONMENT=prod (typo) should raise ValidationError."""
        with pytest.raises(ValidationError, match="environment"):
            Settings(environment="prod")

    def test_rejects_empty_string(self):
        """ENVIRONMENT='' should raise ValidationError."""
        with pytest.raises(ValidationError, match="environment"):
            Settings(environment="")

    def test_rejects_arbitrary_value(self):
        """ENVIRONMENT=fly-production should raise ValidationError."""
        with pytest.raises(ValidationError, match="environment"):
            Settings(environment="fly-production")


class TestMetricsApiKeyValidation:
    """SEC-009: Test minimum length validation on METRICS_API_KEY."""

    def test_accepts_empty_string(self):
        """Empty METRICS_API_KEY means metrics are open (no auth)."""
        settings = Settings(metrics_api_key="")
        assert settings.metrics_api_key == ""

    def test_rejects_short_key(self):
        """METRICS_API_KEY shorter than 16 chars should be rejected."""
        with pytest.raises(ValidationError, match="metrics_api_key"):
            Settings(metrics_api_key="short")

    def test_accepts_16_char_key(self):
        """METRICS_API_KEY with exactly 16 chars should be accepted."""
        key = "a" * 16
        settings = Settings(metrics_api_key=key)
        assert settings.metrics_api_key == key

    def test_accepts_long_key(self):
        """METRICS_API_KEY longer than 16 chars should be accepted."""
        key = "a" * 64
        settings = Settings(metrics_api_key=key)
        assert settings.metrics_api_key == key


class TestStripeKeyPrefixValidation:
    """T11.4: Stripe keys must have valid prefixes when set."""

    def test_accepts_empty_stripe_secret_key(self):
        settings = Settings(stripe_secret_key="")
        assert settings.stripe_secret_key == ""

    def test_accepts_test_mode_key(self):
        settings = Settings(stripe_secret_key="sk_test_abc123")
        assert settings.stripe_secret_key == "sk_test_abc123"

    def test_accepts_live_mode_key(self):
        settings = Settings(stripe_secret_key="sk_live_abc123")
        assert settings.stripe_secret_key == "sk_live_abc123"

    def test_rejects_invalid_prefix(self):
        with pytest.raises(ValidationError, match="stripe_secret_key"):
            Settings(stripe_secret_key="invalid_key_value")

    def test_rejects_publishable_key_in_secret_field(self):
        with pytest.raises(ValidationError, match="stripe_secret_key"):
            Settings(stripe_secret_key="pk_test_abc123")

    def test_accepts_empty_webhook_secret(self):
        settings = Settings(stripe_webhook_secret="")
        assert settings.stripe_webhook_secret == ""

    def test_accepts_valid_webhook_secret(self):
        settings = Settings(stripe_webhook_secret="whsec_abc123")
        assert settings.stripe_webhook_secret == "whsec_abc123"

    def test_rejects_invalid_webhook_prefix(self):
        with pytest.raises(ValidationError, match="stripe_webhook_secret"):
            Settings(stripe_webhook_secret="not_a_webhook_secret")
