from rest_framework import serializers

from accounts.models import MFADevice, Permission, Role, User, UserDevice, UserSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "phone", "first_name", "last_name",
            "avatar", "mfa_enabled", "preferred_language", "timezone", "is_superuser",
        ]
        read_only_fields = ["id", "email", "username", "mfa_enabled", "is_superuser"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "description", "is_active", "priority"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "code", "name", "module", "description"]


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ["id", "ip_address", "is_active", "expires_at", "created_at"]


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ["id", "device_type", "device_name", "is_trusted", "last_used_at"]


class MFADeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFADevice
        fields = ["id", "mfa_type", "name", "is_primary", "is_verified", "last_used_at"]
