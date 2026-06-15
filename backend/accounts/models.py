import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.models import BaseModel, TenantBaseModel


class User(AbstractUser):
    """Platform and estate-scoped user account."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=50, default="UTC")
    metadata = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
        ]

    @property
    def is_deleted(self):
        return not self.is_active

    def get_permission_codes(self, estate_id=None):
        qs = Permission.objects.filter(roles__user_roles__user=self, roles__user_roles__is_active=True)
        if estate_id:
            qs = qs.filter(roles__estate_id=estate_id)
        return set(qs.values_list("code", flat=True))


class Permission(BaseModel):
    """Granular permission definition."""

    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=50, db_index=True)
    is_platform_level = models.BooleanField(default=False)

    class Meta:
        db_table = "accounts_permission"
        ordering = ["module", "code"]
        indexes = [
            models.Index(fields=["module", "code"]),
        ]

    def __str__(self):
        return self.code


class Role(TenantBaseModel):
    """Estate-scoped role with attached permissions."""

    class RoleCode(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        ESTATE_ADMIN = "estate_admin", "Estate Admin"
        FACILITY_ADMIN = "facility_admin", "Facility Admin"
        SECURITY_ADMIN = "security_admin", "Security Admin"
        FINANCE_ADMIN = "finance_admin", "Finance Admin"
        RESIDENT = "resident", "Resident"
        VENDOR = "vendor", "Vendor"
        TECHNICIAN = "technician", "Technician"
        SECURITY_PERSONNEL = "security_personnel", "Security Personnel"

    code = models.CharField(max_length=50, choices=RoleCode.choices, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    priority = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "accounts_role"
        unique_together = [("estate", "code")]
        indexes = [
            models.Index(fields=["estate", "code", "is_active"]),
        ]

    def __str__(self):
        return f"{self.estate_id}:{self.code}"


class UserRole(TenantBaseModel):
    """Assignment of a role to a user within an estate."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_user_role"
        unique_together = [("user", "role", "estate")]
        indexes = [
            models.Index(fields=["user", "estate", "is_active"]),
        ]


User.add_to_class(
    "roles",
    models.ManyToManyField(Role, through=UserRole, through_fields=("user", "role"), related_name="users"),
)
User.add_to_class(
    "estate_memberships",
    models.ManyToManyField(
        "estates.Estate",
        through=UserRole,
        through_fields=("user", "estate"),
        related_name="members",
    ),
)


class UserSession(BaseModel):
    """Active user session tracking."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    estate = models.ForeignKey(
        "estates.Estate",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_sessions",
    )
    refresh_token_jti = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device = models.ForeignKey(
        "accounts.UserDevice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_user_session"
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["expires_at"]),
        ]


class UserDevice(BaseModel):
    """Registered user device for push notifications and MFA."""

    class DeviceType(models.TextChoices):
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"
        WEB = "web", "Web"
        DESKTOP = "desktop", "Desktop"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    device_name = models.CharField(max_length=255, blank=True)
    device_id = models.CharField(max_length=255, db_index=True)
    push_token = models.TextField(blank=True)
    is_trusted = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "accounts_user_device"
        unique_together = [("user", "device_id")]
        indexes = [
            models.Index(fields=["user", "device_type"]),
        ]


class MFADevice(BaseModel):
    """Multi-factor authentication device (TOTP, SMS, email)."""

    class MFAType(models.TextChoices):
        TOTP = "totp", "TOTP Authenticator"
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        BACKUP = "backup", "Backup Codes"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_devices")
    mfa_type = models.CharField(max_length=20, choices=MFAType.choices)
    name = models.CharField(max_length=255, default="Default")
    secret = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts_mfa_device"
        indexes = [
            models.Index(fields=["user", "mfa_type", "is_verified"]),
        ]

    def mark_used(self):
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])
