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


class TestDisplayNameRawStorage:
    """T26.7: display_name stored as raw Unicode — no stripping.

    XSS prevention is handled at output sinks:
    - React JSX auto-escapes text interpolation
    - Email templates use html.escape() if needed
    """

    def test_stores_script_tags_raw(self):
        """Angle brackets are preserved — escaping happens at render time."""
        profile = UserProfileUpdate(display_name="<script>alert(1)</script>")
        assert profile.display_name == "<script>alert(1)</script>"

    def test_normal_name_unchanged(self):
        profile = UserProfileUpdate(display_name="Normal Name")
        assert profile.display_name == "Normal Name"

    def test_stores_html_tags_raw(self):
        profile = UserProfileUpdate(display_name="<b>Bold</b>")
        assert profile.display_name == "<b>Bold</b>"

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

    def test_stores_angle_brackets_raw(self):
        """Angle brackets are no longer stripped."""
        profile = UserProfileUpdate(display_name="<>")
        assert profile.display_name == "<>"

    def test_preserves_unicode(self):
        """Unicode characters are stored as-is, not HTML-escaped."""
        profile = UserProfileUpdate(display_name="Rene Descartes")
        assert profile.display_name == "Rene Descartes"

    def test_preserves_accented_chars(self):
        profile = UserProfileUpdate(display_name="Jose Garcia")
        assert profile.display_name == "Jose Garcia"

    def test_preserves_all_special_chars(self):
        """All special characters stored raw — no stripping at all."""
        profile = UserProfileUpdate(display_name="a<b>c&d\"e'f")
        assert profile.display_name == "a<b>c&d\"e'f"

    def test_max_length_enforced(self):
        """Pydantic max_length=255 still enforces size bounds."""
        with pytest.raises(ValidationError, match="String should have at most 255"):
            UserProfileUpdate(display_name="x" * 256)

    def test_min_length_enforced(self):
        """Pydantic min_length=1 rejects empty strings."""
        with pytest.raises(ValidationError, match="String should have at least 1"):
            UserProfileUpdate(display_name="")
