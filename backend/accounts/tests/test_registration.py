"""Registration with estate selection and admin activation tests."""
import pytest
from rest_framework import status

from accounts.models import Role, User, UserRole
from conftest import TEST_PASSWORD
from notifications.models import Notification
from residents.models import ResidentProfile


@pytest.mark.django_db
class TestRegistrationWithEstate:
    def test_register_creates_pending_resident_profile(self, api_client, estate, unit):
        response = api_client.post(
            "/api/v1/accounts/auth/register/",
            {
                "email": "newresident@test.estateos",
                "password": TEST_PASSWORD,
                "password_confirm": TEST_PASSWORD,
                "first_name": "New",
                "last_name": "Resident",
                "phone": "+2348099999999",
                "estate_id": str(estate.id),
                "unit_id": str(unit.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["has_active_membership"] is False
        assert response.data["pending_membership"] is True
        assert len(response.data["memberships"]) == 1
        assert response.data["memberships"][0]["status"] == "pending"
        assert response.data["memberships"][0]["resident_type"] is None
        assert response.data["memberships"][0]["unit_number"] == unit.unit_number

        profile = ResidentProfile.objects.get(user__email="newresident@test.estateos")
        assert profile.estate_id == estate.id
        assert profile.status == ResidentProfile.Status.PENDING
        assert profile.unit_id == unit.id
        assert profile.resident_type == ""
        assert UserRole.objects.filter(user=profile.user, estate=estate).exists() is False

    def test_register_notifies_estate_admin(self, api_client, estate, unit, admin_user, admin_role):
        UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
        response = api_client.post(
            "/api/v1/accounts/auth/register/",
            {
                "email": "notifyme@test.estateos",
                "password": TEST_PASSWORD,
                "password_confirm": TEST_PASSWORD,
                "first_name": "Notify",
                "last_name": "Me",
                "estate_id": str(estate.id),
                "unit_id": str(unit.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Notification.objects.filter(
            recipient=admin_user,
            estate=estate,
            title="New resident registration",
        ).exists()

    def test_register_requires_estate_and_unit(self, api_client):
        response = api_client.post(
            "/api/v1/accounts/auth/register/",
            {
                "email": "noestate@test.estateos",
                "password": TEST_PASSWORD,
                "password_confirm": TEST_PASSWORD,
                "first_name": "No",
                "last_name": "Estate",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_public_estates_list(self, api_client, estate):
        response = api_client.get("/api/v1/estates/public/")
        assert response.status_code == status.HTTP_200_OK
        assert any(item["id"] == str(estate.id) for item in response.data["results"])

    def test_public_units_list(self, api_client, estate, unit):
        response = api_client.get(f"/api/v1/estates/public/{estate.id}/units/")
        assert response.status_code == status.HTTP_200_OK
        assert any(item["id"] == str(unit.id) for item in response.data["results"])

    def test_register_rejects_occupied_unit(self, api_client, estate, unit, resident):
        response = api_client.post(
            "/api/v1/accounts/auth/register/",
            {
                "email": "blocked@test.estateos",
                "password": TEST_PASSWORD,
                "password_confirm": TEST_PASSWORD,
                "first_name": "Blocked",
                "last_name": "User",
                "estate_id": str(estate.id),
                "unit_id": str(unit.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestResidentActivation:
    def test_admin_can_activate_pending_resident(
        self,
        admin_client,
        estate,
        unit,
        admin_user,
        admin_role,
    ):
        pending_user = User.objects.create_user(
            username="pendingresident",
            email="pending@test.estateos",
            password=TEST_PASSWORD,
            first_name="Pending",
            last_name="Resident",
        )
        profile = ResidentProfile.objects.create(
            estate=estate,
            user=pending_user,
            unit=unit,
            status=ResidentProfile.Status.PENDING,
        )

        response = admin_client.post(
            f"/api/v1/residents/profiles/{profile.id}/activate/",
            {"resident_type": "tenant"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        profile.refresh_from_db()
        assert profile.status == ResidentProfile.Status.ACTIVE
        assert profile.unit_id == unit.id
        assert profile.resident_type == ResidentProfile.ResidentType.TENANT
        assert UserRole.objects.filter(
            user=pending_user,
            estate=estate,
            role__code=Role.RoleCode.RESIDENT,
            is_active=True,
        ).exists()

    def test_activate_requires_resident_type(self, admin_client, estate, unit):
        pending_user = User.objects.create_user(
            username="notype",
            email="notype@test.estateos",
            password=TEST_PASSWORD,
        )
        profile = ResidentProfile.objects.create(
            estate=estate,
            user=pending_user,
            unit=unit,
            status=ResidentProfile.Status.PENDING,
        )
        response = admin_client.post(
            f"/api/v1/residents/profiles/{profile.id}/activate/",
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_includes_membership_status(self, api_client, estate, unit):
        user = User.objects.create_user(
            username="loginpending",
            email="loginpending@test.estateos",
            password=TEST_PASSWORD,
        )
        ResidentProfile.objects.create(
            estate=estate,
            user=user,
            unit=unit,
            status=ResidentProfile.Status.PENDING,
        )
        response = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["pending_membership"] is True
        assert response.data["has_active_membership"] is False
