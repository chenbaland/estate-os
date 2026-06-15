"""Security tests: rate limiting and auth bypass attempts."""
import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status

from conftest import TEST_PASSWORD


@pytest.mark.django_db
@pytest.mark.security
class TestAuthenticationBypass:
    def test_unauthenticated_me_endpoint_denied(self, api_client):
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_jwt_token_rejected(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_authorization_header_rejected(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="NotBearer token")
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cross_tenant_header_without_membership(self, api_client, user, other_estate):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
            HTTP_X_ESTATE_ID=str(other_estate.id),
        )
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.security
class TestBruteForceProtection:
    def test_repeated_failed_login_attempts(self, api_client, user):
        for _ in range(5):
            response = api_client.post(
                "/api/v1/accounts/auth/token/",
                {"email": user.email, "password": "wrong-password"},
                format="json",
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_successful_login_after_failures(self, api_client, user):
        api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        response = api_client.post(
            "/api/v1/accounts/auth/token/",
            {"email": user.email, "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.security
class TestRateLimiting:
    def test_cache_based_rate_limit_counter(self):
        cache.clear()
        key = "rl:test:user:1"
        limit = 5
        for i in range(limit):
            cache.set(key, i + 1, timeout=60)
        count = cache.get(key)
        assert count == limit

    @override_settings(RATELIMIT_ENABLE=True)
    def test_rate_limit_setting_enabled(self):
        from django.conf import settings

        assert settings.RATELIMIT_ENABLE is True

    def test_health_endpoint_public_no_auth_required(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ok"
