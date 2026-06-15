from core.serializers import TenantModelSerializer
from healthcare.models import AmbulanceRequest, Appointment, Hospital, MedicalRecord


class HospitalSerializer(TenantModelSerializer):
    class Meta:
        model = Hospital
        fields = [
            "id",
            "estate",
            "name",
            "slug",
            "description",
            "address",
            "phone",
            "email",
            "website",
            "latitude",
            "longitude",
            "specialties",
            "operating_hours",
            "is_partner",
            "is_active",
            "rating_avg",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "rating_avg", "created_at", "updated_at"]


class AppointmentSerializer(TenantModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "estate",
            "resident",
            "hospital",
            "doctor_name",
            "specialty",
            "status",
            "scheduled_at",
            "duration_minutes",
            "reason",
            "notes",
            "reminder_sent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class AmbulanceRequestSerializer(TenantModelSerializer):
    class Meta:
        model = AmbulanceRequest
        fields = [
            "id",
            "estate",
            "resident",
            "status",
            "priority",
            "pickup_location",
            "destination_hospital",
            "latitude",
            "longitude",
            "patient_condition",
            "dispatched_at",
            "arrived_at",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class MedicalRecordSerializer(TenantModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "estate",
            "resident",
            "hospital",
            "record_type",
            "title",
            "description",
            "record_date",
            "provider_name",
            "attachments",
            "is_confidential",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
