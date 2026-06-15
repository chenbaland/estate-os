import hmac
import logging
import random
import string

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.membership import get_user_memberships
from accounts.auth_serializers import (
    OAuthAuthorizeQuerySerializer,
    OAuthCallbackSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
)
from accounts.models import User, UserDevice, UserSession
from accounts.oauth import (
    exchange_apple_code,
    exchange_google_code,
    get_apple_authorize_url,
    get_google_authorize_url,
    get_or_create_oauth_user,
    verify_apple_identity_token,
    verify_google_id_token,
)
from accounts.serializers import UserDeviceSerializer, UserSerializer, UserSessionSerializer

logger = logging.getLogger("estateos.auth")
OTP_CACHE_PREFIX = "otp:"
OTP_TTL = 600


def _issue_tokens(user, request):
    refresh = RefreshToken.for_user(user)
    if hasattr(request, "estate_id") and request.estate_id:
        refresh["estate_id"] = str(request.estate_id)
    response_data = {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    }
    response_data.update(get_user_memberships(user))
    return response_data


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_issue_tokens(user, request), status=status.HTTP_201_CREATED)


class OTPRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = "".join(random.choices(string.digits, k=6))
        cache.set(f"{OTP_CACHE_PREFIX}{phone}", code, OTP_TTL)

        if settings.DEBUG:
            logger.info("OTP for %s: %s", phone, code)

        return Response({"detail": "OTP sent.", "expires_in": OTP_TTL})


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]
        cached = cache.get(f"{OTP_CACHE_PREFIX}{phone}")

        if not cached or not hmac.compare_digest(str(cached), str(code)):
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(f"{OTP_CACHE_PREFIX}{phone}")
        user, _created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "username": f"user_{phone[-8:]}",
                "email": f"{phone.replace('+', '')}@phone.estateos.local",
                "is_phone_verified": True,
            },
        )
        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])

        return Response(_issue_tokens(user, request))


class GoogleAuthorizeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = OAuthAuthorizeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        url = get_google_authorize_url(state=serializer.validated_data.get("state", ""))
        return Response({"authorization_url": url})


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OAuthCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            if serializer.validated_data.get("id_token"):
                profile = verify_google_id_token(serializer.validated_data["id_token"])
            else:
                tokens = exchange_google_code(serializer.validated_data["code"])
                profile = verify_google_id_token(tokens["id_token"])
        except Exception as exc:
            logger.warning("Google OAuth failed: %s", exc)
            return Response({"detail": "Google authentication failed."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_or_create_oauth_user("google", profile)
        return Response(_issue_tokens(user, request))


class AppleAuthorizeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        serializer = OAuthAuthorizeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        url = get_apple_authorize_url(state=serializer.validated_data.get("state", ""))
        return Response({"authorization_url": url})


class AppleCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OAuthCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            identity_token = serializer.validated_data.get("identity_token") or serializer.validated_data.get("id_token")
            if identity_token:
                profile = verify_apple_identity_token(identity_token)
            else:
                tokens = exchange_apple_code(serializer.validated_data["code"])
                profile = verify_apple_identity_token(tokens["id_token"])
        except Exception as exc:
            logger.warning("Apple OAuth failed: %s", exc)
            return Response({"detail": "Apple authentication failed."}, status=status.HTTP_400_BAD_REQUEST)

        email = profile.get("email")
        if not email and profile.get("sub"):
            email = f"{profile['sub']}@privaterelay.appleid.com"
        profile["email"] = email
        user = get_or_create_oauth_user("apple", profile)
        return Response(_issue_tokens(user, request))


class SessionListView(APIView):
    def get(self, request):
        sessions = UserSession.objects.filter(user=request.user, is_active=True).order_by("-created_at")
        return Response(UserSessionSerializer(sessions, many=True).data)


class SessionRevokeView(APIView):
    def delete(self, request, session_id):
        try:
            session = UserSession.objects.get(id=session_id, user=request.user)
        except UserSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        session.is_active = False
        session.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceListView(APIView):
    def get(self, request):
        devices = UserDevice.objects.filter(user=request.user)
        return Response(UserDeviceSerializer(devices, many=True).data)

    def post(self, request):
        serializer = UserDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device, _ = UserDevice.objects.update_or_create(
            user=request.user,
            device_id=request.data.get("device_id"),
            defaults=serializer.validated_data,
        )
        return Response(UserDeviceSerializer(device).data, status=status.HTTP_201_CREATED)


class DeviceRevokeView(APIView):
    def delete(self, request, device_id):
        deleted, _ = UserDevice.objects.filter(user=request.user, id=device_id).delete()
        if not deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)
