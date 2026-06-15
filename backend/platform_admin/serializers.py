from rest_framework import serializers

from accounts.models import Role, User, UserRole
from estates.models import Estate
from platform_admin.models import PlatformAuditLog
from platform_admin.emails import send_admin_assignment_email
from platform_admin.services import ADMIN_ROLE_CODES, assign_estate_admin, create_estate, unique_estate_slug


class PlatformOverviewSerializer(serializers.Serializer):
    estates_total = serializers.IntegerField()
    estates_active = serializers.IntegerField()
    users_total = serializers.IntegerField()
    estate_admins_total = serializers.IntegerField()
    pending_registrations = serializers.IntegerField()
    units_total = serializers.IntegerField()


class PlatformEstateSerializer(serializers.ModelSerializer):
    admin_count = serializers.SerializerMethodField()
    pending_residents = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = [
            "id",
            "name",
            "slug",
            "estate_type",
            "tier",
            "description",
            "city",
            "state",
            "country",
            "address_line1",
            "address_line2",
            "contact_email",
            "contact_phone",
            "timezone",
            "currency",
            "total_units",
            "occupied_units",
            "is_active",
            "onboarded_at",
            "admin_count",
            "pending_residents",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "onboarded_at", "created_at", "updated_at"]

    def get_admin_count(self, obj):
        return UserRole.objects.filter(
            estate=obj,
            is_active=True,
            role__code__in=ADMIN_ROLE_CODES,
        ).count()

    def get_pending_residents(self, obj):
        from residents.models import ResidentProfile

        return ResidentProfile.objects.filter(
            estate=obj,
            status=ResidentProfile.Status.PENDING,
        ).count()


class PlatformEstateCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = Estate
        fields = [
            "name",
            "slug",
            "estate_type",
            "tier",
            "description",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "country",
            "contact_email",
            "contact_phone",
            "timezone",
            "currency",
            "total_units",
            "is_active",
        ]

    def validate_slug(self, value):
        slug = value or unique_estate_slug(self.initial_data.get("name", "estate"))
        if Estate.all_objects.filter(slug=slug).exists():
            raise serializers.ValidationError("An estate with this slug already exists.")
        return slug

    def create(self, validated_data):
        return create_estate(validated_data)


class PlatformEstateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = [
            "name",
            "estate_type",
            "tier",
            "description",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "country",
            "contact_email",
            "contact_phone",
            "timezone",
            "currency",
            "total_units",
            "is_active",
        ]


class PlatformAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    estate_id = serializers.UUIDField(read_only=True)
    estate_name = serializers.CharField(source="estate.name", read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = UserRole
        fields = [
            "id",
            "user_id",
            "user_email",
            "user_first_name",
            "user_last_name",
            "estate_id",
            "estate_name",
            "role_code",
            "role_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class PlatformAuditLogSerializer(serializers.ModelSerializer):
    actor_id = serializers.UUIDField(source="actor.id", read_only=True, allow_null=True)
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)
    actor_name = serializers.SerializerMethodField()
    estate_id = serializers.UUIDField(source="estate.id", read_only=True, allow_null=True)
    estate_name = serializers.CharField(source="estate.name", read_only=True, allow_null=True)

    class Meta:
        model = PlatformAuditLog
        fields = [
            "id",
            "action",
            "resource_type",
            "resource_id",
            "actor_id",
            "actor_email",
            "actor_name",
            "estate_id",
            "estate_name",
            "summary",
            "metadata",
            "ip_address",
            "trace_id",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_name(self, obj):
        if not obj.actor:
            return None
        name = obj.actor.get_full_name()
        return name or obj.actor.email


class AssignPlatformAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    estate_id = serializers.UUIDField()
    role_code = serializers.ChoiceField(
        choices=[
            (Role.RoleCode.ESTATE_ADMIN, "Estate Admin"),
            (Role.RoleCode.FINANCE_ADMIN, "Finance Admin"),
            (Role.RoleCode.SECURITY_ADMIN, "Security Admin"),
            (Role.RoleCode.FACILITY_ADMIN, "Facility Admin"),
        ],
        default=Role.RoleCode.ESTATE_ADMIN,
    )

    def validate_estate_id(self, value):
        try:
            estate = Estate.objects.get(id=value, is_deleted=False)
        except Estate.DoesNotExist as exc:
            raise serializers.ValidationError("Estate not found.") from exc
        self.context["estate"] = estate
        return value

    def create(self, validated_data):
        estate = self.context["estate"]
        assigned_by = self.context["request"].user
        try:
            result = assign_estate_admin(
                email=validated_data["email"],
                estate=estate,
                role_code=validated_data["role_code"],
                assigned_by=assigned_by,
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
        except Role.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"role_code": "Role is not configured for this estate."},
            ) from exc

        send_admin_assignment_email(
            user=result.user,
            estate=estate,
            role_name=result.user_role.role.name,
            assigned_by=assigned_by,
            is_new_user=result.created_user,
            temporary_password=result.temporary_password,
        )
        return result.user_role
