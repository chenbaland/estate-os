from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import MFADevice, Permission, Role, User, UserDevice, UserRole, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "phone", "is_active", "mfa_enabled", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser", "mfa_enabled")
    search_fields = ("email", "username", "phone")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("EstateOS", {"fields": ("phone", "avatar", "mfa_enabled", "preferred_language", "timezone")}),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module", "is_platform_level")
    list_filter = ("module", "is_platform_level")
    search_fields = ("code", "name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "estate", "is_active", "priority")
    list_filter = ("code", "is_active", "is_system_role")
    filter_horizontal = ("permissions",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "estate", "is_active", "expires_at")
    list_filter = ("is_active",)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "is_active", "expires_at")
    list_filter = ("is_active",)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_type", "device_name", "is_trusted", "last_used_at")


@admin.register(MFADevice)
class MFADeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "mfa_type", "name", "is_primary", "is_verified")
