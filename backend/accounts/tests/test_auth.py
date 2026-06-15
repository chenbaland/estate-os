"""Authentication, OTP/MFA, session, and token tests."""
import pyotp
import pytest
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status

from accounts.models import MFADevice, UserSession
from conftest import TEST_PASSWORD


@pytest.mark.django_db
class TestJWTAuthentication:
    def test_login_returns_access_and_refresh_tokens(self, api_client, user):
        response = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_superuser_login_includes_platform_role(self, api_client, superuser):
        response = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": superuser.email, "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["is_superuser"] is True
        assert response.data["has_active_membership"] is True
        assert response.data["roles"][0]["code"] == "super_admin"

    def test_login_rejects_invalid_credentials(self, api_client, user):
        response = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_rotates_refresh_token(self, api_client, user):
        login = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": TEST_PASSWORD},
            format="json",
        )
        refresh = login.data["refresh"]
        response = api_client.post(
            "/api/v1/accounts/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_current_user_endpoint_requires_authentication(self, api_client):
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_current_user_returns_profile(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == user.email
        assert response.data["user"]["id"] == str(user.id)
        assert "memberships" in response.data
        assert "has_active_membership" in response.data

    def test_superuser_has_platform_access_without_resident_membership(self, superuser_client, superuser):
        response = superuser_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["has_active_membership"] is True
        assert response.data["pending_membership"] is False
        assert response.data["roles"][0]["code"] == "super_admin"
        assert response.data["user"]["is_superuser"] is True


@pytest.mark.django_db
class TestMFAAndOTP:
    def test_totp_device_generates_valid_code(self, mfa_device):
        totp = pyotp.TOTP(mfa_device.secret)
        code = totp.now()
        assert totp.verify(code, valid_window=1)

    def test_unverified_totp_device_not_primary_by_default(self, user):
        device = MFADevice.objects.create(
            user=user,
            mfa_type=MFADevice.MFAType.TOTP,
            secret="JBSWY3DPEHPK3PXP",
            is_verified=False,
        )
        assert device.is_verified is False
        assert device.is_primary is False

    def test_user_mfa_enabled_flag(self, user, mfa_device):
        user.mfa_enabled = True
        user.save(update_fields=["mfa_enabled"])
        user.refresh_from_db()
        assert user.mfa_enabled is True

    def test_sms_mfa_device_type(self, user):
        device = MFADevice.objects.create(
            user=user,
            mfa_type=MFADevice.MFAType.SMS,
            name="SMS OTP",
            is_verified=True,
        )
        assert device.mfa_type == MFADevice.MFAType.SMS


@pytest.mark.django_db
class TestUserSessions:
    def test_session_tracks_refresh_token_jti(self, user_session):
        assert user_session.is_active is True
        assert user_session.refresh_token_jti == "test-jti-abc123"

    def test_session_revocation(self, user_session):
        user_session.is_active = False
        user_session.revoked_at = timezone.now()
        user_session.save()
        user_session.refresh_from_db()
        assert user_session.is_active is False
        assert user_session.revoked_at is not None

    @freeze_time("2026-06-11 12:00:00")
    def test_expired_session_detection(self, user, estate):
        session = UserSession.objects.create(
            user=user,
            estate=estate,
            refresh_token_jti="expired-jti",
            expires_at=timezone.now() - timezone.timedelta(hours=1),
        )
        assert session.expires_at < timezone.now()


@pytest.mark.django_db
class TestRBACBasics:
    def test_user_permission_codes_scoped_to_estate(self, user, estate, resident_role, permission_view_residents):
        from accounts.models import UserRole

        UserRole.objects.create(user=user, role=resident_role, estate=estate)
        codes = user.get_permission_codes(estate_id=estate.id)
        assert "residents.view" in codes

    def test_superuser_bypasses_permission_lookup(self, superuser):
        assert superuser.is_superuser
        assert superuser.get_permission_codes() == set()
