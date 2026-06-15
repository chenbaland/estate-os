"""RBAC permission checks and cross-tenant denial tests."""
import pytest
from rest_framework.test import APIRequestFactory

from accounts.models import Role, UserRole
from core.permissions import (
    HasPermission,
    HasRole,
    IsEstateAdmin,
    IsSuperAdmin,
    IsTenantMember,
)


@pytest.fixture
def request_factory():
    return APIRequestFactory()


def _make_request(factory, user, estate=None, method="get", path="/api/v1/test/"):
    request = getattr(factory, method)(path)
    request.user = user
    if estate:
        request.estate_id = estate.id
        request.estate = estate
    return request


@pytest.mark.django_db
class TestIsSuperAdmin:
    def test_superuser_has_access(self, request_factory, superuser):
        request = _make_request(request_factory, superuser)
        assert IsSuperAdmin().has_permission(request, None) is True

    def test_regular_user_denied(self, request_factory, user):
        request = _make_request(request_factory, user)
        assert IsSuperAdmin().has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEstateAdmin:
    def test_estate_admin_granted(self, request_factory, admin_user, estate, admin_role):
        UserRole.objects.get_or_create(user=admin_user, role=admin_role, estate=estate)
        request = _make_request(request_factory, admin_user, estate)
        assert IsEstateAdmin().has_permission(request, None) is True

    def test_resident_denied(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        assert IsEstateAdmin().has_permission(request, None) is False


@pytest.mark.django_db
class TestHasRole:
    def test_matching_role_granted(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        permission = HasRole()
        permission.required_roles = [Role.RoleCode.RESIDENT]
        assert permission.has_permission(request, None) is True

    def test_missing_role_denied(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        permission = HasRole()
        permission.required_roles = [Role.RoleCode.SECURITY_PERSONNEL]
        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestHasPermission:
    def test_granted_when_user_has_all_permissions(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        permission = HasPermission()
        permission.required_permissions = ["residents.view"]
        assert permission.has_permission(request, None) is True

    def test_denied_when_permission_missing(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        permission = HasPermission()
        permission.required_permissions = ["billing.refund"]
        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsTenantMember:
    def test_member_of_estate_granted(self, request_factory, user, estate, resident_role):
        UserRole.objects.get_or_create(user=user, role=resident_role, estate=estate)
        request = _make_request(request_factory, user, estate)
        assert IsTenantMember().has_permission(request, None) is True

    def test_non_member_denied(self, request_factory, user, estate):
        request = _make_request(request_factory, user, estate)
        assert IsTenantMember().has_permission(request, None) is False


@pytest.mark.django_db
class TestCrossTenantDenial:
    def test_user_role_in_other_estate_not_counted(self, request_factory, user, estate, other_estate):
        other_role = Role.objects.create(
            estate=other_estate,
            code=Role.RoleCode.ESTATE_ADMIN,
            name="Other Estate Admin",
        )
        UserRole.objects.create(user=user, role=other_role, estate=other_estate)
        request = _make_request(request_factory, user, estate)
        assert IsEstateAdmin().has_permission(request, None) is False

    def test_permissions_scoped_to_wrong_estate(self, user, estate, other_estate, permission_view_residents):
        other_role = Role.objects.create(
            estate=other_estate,
            code=Role.RoleCode.RESIDENT,
            name="Other Resident",
        )
        other_role.permissions.add(permission_view_residents)
        UserRole.objects.create(user=user, role=other_role, estate=other_estate)
        codes = user.get_permission_codes(estate_id=estate.id)
        assert "residents.view" not in codes

    def test_cross_tenant_membership_check(self, request_factory, user, estate, other_estate, resident_role):
        other_role = Role.objects.create(
            estate=other_estate,
            code=Role.RoleCode.RESIDENT,
            name="Other Resident",
        )
        UserRole.objects.create(user=user, role=other_role, estate=other_estate)
        request = _make_request(request_factory, user, estate)
        assert IsTenantMember().has_permission(request, None) is False
