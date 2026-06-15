from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login accepting email + password."""

    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(required=False)
        if "username" in self.fields:
            del self.fields["username"]

    def validate(self, attrs):
        email = attrs.get("email") or attrs.get(User.USERNAME_FIELD)
        if email:
            attrs[User.USERNAME_FIELD] = email
        data = super().validate(attrs)
        from accounts.membership import get_user_memberships
        from accounts.serializers import UserSerializer

        data.update(get_user_memberships(self.user))
        data["user"] = UserSerializer(self.user).data
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirm = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)
    estate_id = serializers.UUIDField(write_only=True)
    unit_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "estate_id",
            "unit_id",
        ]

    def validate_estate_id(self, value):
        from estates.models import Estate

        try:
            estate = Estate.objects.get(id=value, is_deleted=False, is_active=True)
        except Estate.DoesNotExist as exc:
            raise serializers.ValidationError("Select a valid active estate.") from exc
        self.context["estate"] = estate
        return value

    def validate_unit_id(self, value):
        from estates.models import Unit

        estate = self.context.get("estate")
        if estate is None:
            raise serializers.ValidationError("Select an estate before choosing a unit.")

        try:
            unit = Unit.objects.get(
                id=value,
                estate=estate,
                is_deleted=False,
                is_active=True,
            )
        except Unit.DoesNotExist as exc:
            raise serializers.ValidationError("Select a valid unit in this estate.") from exc

        if unit.occupancy_status != Unit.OccupancyStatus.VACANT:
            raise serializers.ValidationError("This unit is not available.")

        from residents.models import ResidentProfile

        if ResidentProfile.objects.filter(
            unit=unit,
            status__in=[ResidentProfile.Status.PENDING, ResidentProfile.Status.ACTIVE],
        ).exists():
            raise serializers.ValidationError("This unit already has a resident assigned.")

        self.context["unit"] = unit
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])

        if not attrs.get("username"):
            base = attrs["email"].split("@")[0][:140]
            username = base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1
            attrs["username"] = username

        return attrs

    def create(self, validated_data):
        from django.db import transaction

        from accounts.membership import register_resident_for_estate

        estate = self.context["estate"]
        unit = self.context["unit"]
        validated_data.pop("unit_id")
        validated_data.pop("estate_id")
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            try:
                profile = register_resident_for_estate(
                    user,
                    estate,
                    unit=unit,
                )
            except ValueError as exc:
                raise serializers.ValidationError({"unit_id": str(exc)}) from exc

        self.context["resident_profile"] = profile
        self.context["estate"] = estate
        return user


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6, min_length=4)


class OAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    id_token = serializers.CharField(required=False)
    identity_token = serializers.CharField(required=False)

    def validate(self, attrs):
        if not any(attrs.get(k) for k in ("code", "id_token", "identity_token")):
            raise serializers.ValidationError("Provide code, id_token, or identity_token.")
        return attrs


class OAuthAuthorizeQuerySerializer(serializers.Serializer):
    state = serializers.CharField(required=False, allow_blank=True, default="")
