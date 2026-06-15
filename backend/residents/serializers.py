from rest_framework import serializers

from core.serializers import TenantModelSerializer
from residents.models import DomesticStaff, FamilyMember, ResidentProfile, Vehicle


class ResidentProfileSerializer(TenantModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)

    class Meta:
        model = ResidentProfile
        fields = [
            "id",
            "estate",
            "user",
            "user_email",
            "user_first_name",
            "user_last_name",
            "unit",
            "unit_number",
            "resident_type",
            "status",
            "move_in_date",
            "move_out_date",
            "emergency_contact_name",
            "emergency_contact_phone",
            "id_document_type",
            "id_document_number",
            "id_document_file",
            "is_primary",
            "notes",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class FamilyMemberSerializer(TenantModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            "id",
            "estate",
            "primary_resident",
            "user",
            "full_name",
            "relationship",
            "date_of_birth",
            "phone",
            "email",
            "photo",
            "has_gate_access",
            "access_expires_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class DomesticStaffSerializer(TenantModelSerializer):
    class Meta:
        model = DomesticStaff
        fields = [
            "id",
            "estate",
            "employer",
            "full_name",
            "role",
            "phone",
            "photo",
            "id_document_number",
            "has_gate_access",
            "access_schedule",
            "employment_start",
            "employment_end",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class VehicleSerializer(TenantModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "estate",
            "owner",
            "vehicle_type",
            "make",
            "model",
            "color",
            "license_plate",
            "registration_number",
            "registration_expiry",
            "rfid_tag",
            "is_ev",
            "is_active",
            "photo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
