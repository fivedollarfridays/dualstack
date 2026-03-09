"""Tests for RBAC role definitions, permission sets, and helpers."""

import pytest

from app.core.rbac import (
    ROLE_PERMISSIONS,
    Role,
    has_permission,
)


class TestRoleEnum:
    """Role enum has ADMIN and MEMBER values."""

    def test_admin_value(self):
        assert Role.ADMIN.value == "admin"

    def test_member_value(self):
        assert Role.MEMBER.value == "member"

    def test_role_from_string(self):
        assert Role("admin") is Role.ADMIN
        assert Role("member") is Role.MEMBER

    def test_invalid_role_raises(self):
        with pytest.raises(ValueError):
            Role("superadmin")


class TestRolePermissions:
    """ROLE_PERMISSIONS maps each role to a set of permission strings."""

    def test_admin_has_permissions(self):
        assert isinstance(ROLE_PERMISSIONS[Role.ADMIN], set)
        assert len(ROLE_PERMISSIONS[Role.ADMIN]) > 0

    def test_member_has_permissions(self):
        assert isinstance(ROLE_PERMISSIONS[Role.MEMBER], set)
        assert len(ROLE_PERMISSIONS[Role.MEMBER]) > 0

    def test_admin_superset_of_member(self):
        """Admin has all permissions that member has, plus admin-specific ones."""
        assert ROLE_PERMISSIONS[Role.MEMBER].issubset(ROLE_PERMISSIONS[Role.ADMIN])
        assert ROLE_PERMISSIONS[Role.ADMIN] != ROLE_PERMISSIONS[Role.MEMBER]

    def test_admin_has_admin_specific_permissions(self):
        admin_only = ROLE_PERMISSIONS[Role.ADMIN] - ROLE_PERMISSIONS[Role.MEMBER]
        assert "users:manage" in admin_only
        assert "admin:access" in admin_only

    def test_member_has_basic_permissions(self):
        assert "profile:read" in ROLE_PERMISSIONS[Role.MEMBER]
        assert "profile:update" in ROLE_PERMISSIONS[Role.MEMBER]


class TestHasPermission:
    """has_permission(role, permission) checks role permission sets."""

    def test_admin_has_admin_permission(self):
        assert has_permission(Role.ADMIN, "admin:access") is True

    def test_member_lacks_admin_permission(self):
        assert has_permission(Role.MEMBER, "admin:access") is False

    def test_member_has_own_permission(self):
        assert has_permission(Role.MEMBER, "profile:read") is True

    def test_admin_has_member_permission(self):
        assert has_permission(Role.ADMIN, "profile:read") is True

    def test_nonexistent_permission(self):
        assert has_permission(Role.ADMIN, "nonexistent:perm") is False

    def test_string_role_converted(self):
        """has_permission accepts string role values too."""
        assert has_permission("admin", "admin:access") is True
        assert has_permission("member", "admin:access") is False
