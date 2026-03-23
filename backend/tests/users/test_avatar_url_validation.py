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
    """T25.7: display_name strips < and > but stores raw Unicode (no HTML entities)."""

    def test_strips_script_tags(self):
        profile = UserProfileUpdate(display_name="<script>alert(1)</script>")
        assert profile.display_name == "scriptalert(1)/script"

    def test_normal_name_unchanged(self):
        profile = UserProfileUpdate(display_name="Normal Name")
        assert profile.display_name == "Normal Name"

    def test_strips_html_tags(self):
        profile = UserProfileUpdate(display_name="<b>Bold</b>")
        assert profile.display_name == "bBold/b"

    def test_preserves_quotes(self):
        """Quotes are stored raw — no HTML entity encoding."""
        profile = UserProfileUpdate(display_name='He said "hello"')
        assert profile.display_name == 'He said "hello"'

    def test_preserves_ampersand(self):
        """Ampersands are stored raw — no &amp; encoding."""
        profile = UserProfileUpdate(display_name="Tom & Jerry")
        assert profile.display_name == "Tom & Jerry"

    def test_none_unchanged(self):
        profile = UserProfileUpdate(display_name=None)
        assert profile.display_name is None

    def test_angle_brackets_stripped(self):
        profile = UserProfileUpdate(display_name="<>")
        assert profile.display_name == ""

    def test_preserves_unicode(self):
        """Unicode characters are stored as-is, not HTML-escaped."""
        profile = UserProfileUpdate(display_name="Rene Descartes")
        assert profile.display_name == "Rene Descartes"

    def test_preserves_accented_chars(self):
        profile = UserProfileUpdate(display_name="Jose Garcia")
        assert profile.display_name == "Jose Garcia"

    def test_strips_angle_brackets_only(self):
        """Only < and > are removed; other special chars remain."""
        profile = UserProfileUpdate(display_name="a<b>c&d\"e'f")
        assert profile.display_name == "abc&d\"e'f"
