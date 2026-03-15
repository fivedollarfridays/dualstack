"""Tests for avatar URL validation in UserProfileUpdate schema."""

import pytest
from pydantic import ValidationError

from app.users.schemas import UserProfileUpdate


class TestAvatarUrlRejectsUnsafeSchemes:
    def test_rejects_javascript_scheme(self):
        with pytest.raises(ValidationError, match="HTTPS"):
            UserProfileUpdate(avatar_url="javascript:alert(1)")

    def test_rejects_data_scheme(self):
        with pytest.raises(ValidationError, match="HTTPS"):
            UserProfileUpdate(avatar_url="data:text/html,<script>alert(1)</script>")

    def test_rejects_http_scheme(self):
        with pytest.raises(ValidationError, match="HTTPS"):
            UserProfileUpdate(avatar_url="http://example.com/img.png")


class TestAvatarUrlAcceptsValidValues:
    def test_accepts_https_url(self):
        profile = UserProfileUpdate(avatar_url="https://example.com/img.png")
        assert profile.avatar_url == "https://example.com/img.png"

    def test_accepts_none(self):
        profile = UserProfileUpdate(avatar_url=None)
        assert profile.avatar_url is None

    def test_accepts_omitted(self):
        profile = UserProfileUpdate(display_name="Alice")
        assert profile.avatar_url is None


class TestAvatarUrlEdgeCases:
    def test_rejects_scheme_with_no_host(self):
        with pytest.raises(ValidationError, match="valid host"):
            UserProfileUpdate(avatar_url="https://")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValidationError, match="HTTPS"):
            UserProfileUpdate(avatar_url="ftp://files.example.com/img.png")
