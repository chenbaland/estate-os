"""Platform super-admin API tests."""
import pytest
from django.core import mail
from rest_framework import status

from accounts.models import Role, UserRole
from conftest import TEST_PASSWORD
from estates.models import Estate
from platform_admin.models import PlatformAuditLog


@pytest.fixture
def superuser_client(api_client, superuser):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(superuser)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.mark.django_db
class TestPlatformOverview:
    def test_overview_requires_superuser(self, authenticated_client):
        response = authenticated_client.get("/api/v1/platform/overview/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_overview_returns_stats(self, superuser_client, estate, admin_user, admin_role):
        UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
        response = superuser_client.get("/api/v1/platform/overview/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["estates_total"] >= 1
        assert response.data["users_total"] >= 1


@pytest.mark.django_db
class TestPlatformEstates:
    def test_create_estate(self, superuser_client):
        response = superuser_client.post(
            "/api/v1/platform/estates/",
            {
                "name": "Harbour View",
                "address_line1": "10 Marina Road",
                "city": "Lagos",
                "state": "Lagos",
                "country": "NG",
                "contact_email": "admin@harbourview.test",
                "total_units": 120,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        estate = Estate.objects.get(slug=response.data["slug"])
        assert estate.name == "Harbour View"
        assert Role.objects.filter(estate=estate, code=Role.RoleCode.ESTATE_ADMIN).exists()
        assert PlatformAuditLog.objects.filter(
            action=PlatformAuditLog.Action.ESTATE_CREATED,
            resource_id=estate.id,
        ).exists()

    def test_list_estates(self, superuser_client, estate):
        response = superuser_client.get("/api/v1/platform/estates/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_update_estate(self, superuser_client, estate):
        response = superuser_client.patch(
            f"/api/v1/platform/estates/{estate.id}/",
            {"name": "Updated Estate Name", "total_units": 50},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        estate.refresh_from_db()
        assert estate.name == "Updated Estate Name"
        assert estate.total_units == 50
        assert PlatformAuditLog.objects.filter(
            action=PlatformAuditLog.Action.ESTATE_UPDATED,
            resource_id=estate.id,
        ).exists()

    def test_deactivate_estate(self, superuser_client, estate):
        response = superuser_client.post(
            f"/api/v1/platform/estates/{estate.id}/deactivate/",
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        estate.refresh_from_db()
        assert estate.is_active is False
        assert PlatformAuditLog.objects.filter(
            action=PlatformAuditLog.Action.ESTATE_DEACTIVATED,
            resource_id=estate.id,
        ).exists()

    def test_activate_estate(self, superuser_client, estate):
        estate.is_active = False
        estate.save(update_fields=["is_active", "updated_at"])
        response = superuser_client.post(
            f"/api/v1/platform/estates/{estate.id}/activate/",
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        estate.refresh_from_db()
        assert estate.is_active is True


@pytest.mark.django_db
class TestPlatformAdmins:
    def test_assign_estate_admin(self, superuser_client, estate, superuser):
        response = superuser_client.post(
            "/api/v1/platform/admins/",
            {
                "email": "newadmin@test.estateos",
                "first_name": "New",
                "last_name": "Admin",
                "estate_id": str(estate.id),
                "role_code": Role.RoleCode.ESTATE_ADMIN,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert UserRole.objects.filter(
            user__email="newadmin@test.estateos",
            estate=estate,
            role__code=Role.RoleCode.ESTATE_ADMIN,
            is_active=True,
        ).exists()
        assert len(mail.outbox) == 1
        assert "newadmin@test.estateos" in mail.outbox[0].to
        assert PlatformAuditLog.objects.filter(
            action=PlatformAuditLog.Action.ADMIN_ASSIGNED,
        ).exists()

    def test_list_admins(self, superuser_client, estate, admin_user, admin_role):
        UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
        response = superuser_client.get("/api/v1/platform/admins/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_revoke_admin(self, superuser_client, estate, admin_user, admin_role):
        user_role = UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
        response = superuser_client.delete(f"/api/v1/platform/admins/{user_role.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user_role.refresh_from_db()
        assert user_role.is_active is False
        assert PlatformAuditLog.objects.filter(
            action=PlatformAuditLog.Action.ADMIN_REVOKED,
            resource_id=user_role.id,
        ).exists()


@pytest.mark.django_db
class TestPlatformAuditLogs:
    def test_audit_logs_require_superuser(self, authenticated_client):
        response = authenticated_client.get("/api/v1/platform/audit-logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_audit_logs(self, superuser_client, estate):
        PlatformAuditLog.objects.create(
            action=PlatformAuditLog.Action.ESTATE_UPDATED,
            resource_type="estate",
            resource_id=estate.id,
            estate=estate,
            summary=f"Updated estate {estate.name}",
        )
        response = superuser_client.get("/api/v1/platform/audit-logs/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        assert response.data["results"][0]["summary"]
