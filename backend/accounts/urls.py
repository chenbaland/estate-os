from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.auth_views import (
    AppleAuthorizeView,
    AppleCallbackView,
    DeviceListView,
    DeviceRevokeView,
    GoogleAuthorizeView,
    GoogleCallbackView,
    LogoutView,
    OTPRequestView,
    OTPVerifyView,
    RegisterView,
    SessionListView,
    SessionRevokeView,
)
from accounts.views import CurrentUserView, EmailTokenObtainPairView, PermissionViewSet, RoleViewSet

router = DefaultRouter()
router.register("permissions", PermissionViewSet, basename="permission")
router.register("roles", RoleViewSet, basename="role")

urlpatterns = [
    path("auth/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/otp/request/", OTPRequestView.as_view(), name="otp-request"),
    path("auth/otp/verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path("auth/oauth/google/authorize/", GoogleAuthorizeView.as_view(), name="google-authorize"),
    path("auth/oauth/google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("auth/oauth/apple/authorize/", AppleAuthorizeView.as_view(), name="apple-authorize"),
    path("auth/oauth/apple/callback/", AppleCallbackView.as_view(), name="apple-callback"),
    path("auth/sessions/", SessionListView.as_view(), name="session-list"),
    path("auth/sessions/<uuid:session_id>/", SessionRevokeView.as_view(), name="session-revoke"),
    path("auth/devices/", DeviceListView.as_view(), name="device-list"),
    path("auth/devices/<uuid:device_id>/", DeviceRevokeView.as_view(), name="device-revoke"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("", include(router.urls)),
]
