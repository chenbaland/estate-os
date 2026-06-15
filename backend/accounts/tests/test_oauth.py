"""OAuth provider tests."""
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestGoogleOAuth:
    @patch("accounts.auth_views.get_google_authorize_url")
    def test_google_authorize_returns_url(self, mock_url, api_client):
        mock_url.return_value = "https://accounts.google.com/o/oauth2/auth?client_id=test"
        response = api_client.get("/api/v1/accounts/auth/oauth/google/authorize/")
        assert response.status_code == status.HTTP_200_OK
        assert "authorization_url" in response.data

    @patch("accounts.auth_views.verify_google_id_token")
    @patch("accounts.auth_views.get_or_create_oauth_user")
    def test_google_callback_with_id_token(self, mock_user, mock_verify, api_client, user):
        mock_verify.return_value = {"email": "oauth@test.com", "sub": "google123"}
        mock_user.return_value = user
        response = api_client.post(
            "/api/v1/accounts/auth/oauth/google/callback/",
            {"id_token": "fake-token"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert "roles" in response.data
        assert "has_active_membership" in response.data


@pytest.mark.django_db
class TestAppleOAuth:
    @patch("accounts.auth_views.get_apple_authorize_url")
    def test_apple_authorize_returns_url(self, mock_url, api_client):
        mock_url.return_value = "https://appleid.apple.com/auth/authorize?client_id=test"
        response = api_client.get("/api/v1/accounts/auth/oauth/apple/authorize/")
        assert response.status_code == status.HTTP_200_OK
        assert "authorization_url" in response.data

    @patch("accounts.auth_views.verify_apple_identity_token")
    @patch("accounts.auth_views.get_or_create_oauth_user")
    def test_apple_callback_with_identity_token(self, mock_user, mock_verify, api_client, user):
        mock_verify.return_value = {"email": "apple@test.com", "sub": "apple456"}
        mock_user.return_value = user
        response = api_client.post(
            "/api/v1/accounts/auth/oauth/apple/callback/",
            {"identity_token": "fake-apple-token"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
class TestRegisterAndOTP:
    def test_register_creates_user(self, api_client, estate, unit):
        response = api_client.post(
            "/api/v1/accounts/auth/register/",
            {
                "email": "newuser@test.estateos",
                "username": "newuser",
                "password": "securepass12345",
                "password_confirm": "securepass12345",
                "first_name": "New",
                "last_name": "User",
                "estate_id": str(estate.id),
                "unit_id": str(unit.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert response.data["pending_membership"] is True

    @patch("accounts.auth_views.cache")
    def test_otp_verify_issues_tokens(self, mock_cache, api_client, user):
        mock_cache.get.return_value = "123456"
        user.phone = "+2348099999999"
        user.save()
        response = api_client.post(
            "/api/v1/accounts/auth/otp/verify/",
            {"phone": user.phone, "code": "123456"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
