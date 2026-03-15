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


class TestDisplayNameSanitization:
    """T19.5: display_name must strip < and > to prevent stored XSS."""

    def test_strips_script_tags(self):
        profile = UserProfileUpdate(display_name="<script>alert(1)</script>")
        assert profile.display_name == "scriptalert(1)/script"

    def test_normal_name_unchanged(self):
        profile = UserProfileUpdate(display_name="Normal Name")
        assert profile.display_name == "Normal Name"

    def test_strips_html_tags(self):
        profile = UserProfileUpdate(display_name="<b>Bold</b>")
        assert profile.display_name == "bBold/b"

    def test_none_unchanged(self):
        profile = UserProfileUpdate(display_name=None)
        assert profile.display_name is None

    def test_angle_brackets_only_stripped_to_empty(self):
        """A name of only angle brackets becomes empty string after stripping."""
        profile = UserProfileUpdate(display_name="<>")
        assert profile.display_name == ""
