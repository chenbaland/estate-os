from core.serializers import TenantModelSerializer
from pharmacy.models import DrugReminder, MedicationOrder, Prescription


class PrescriptionSerializer(TenantModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "estate",
            "resident",
            "doctor_name",
            "hospital_name",
            "prescription_number",
            "status",
            "image",
            "medications",
            "issued_date",
            "expiry_date",
            "verified_by",
            "verified_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class MedicationOrderSerializer(TenantModelSerializer):
    class Meta:
        model = MedicationOrder
        fields = [
            "id",
            "estate",
            "prescription",
            "resident",
            "order_number",
            "status",
            "items",
            "total_amount",
            "currency",
            "delivery_type",
            "delivery_address",
            "payment_reference",
            "fulfilled_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class DrugReminderSerializer(TenantModelSerializer):
    class Meta:
        model = DrugReminder
        fields = [
            "id",
            "estate",
            "resident",
            "medication_name",
            "dosage",
            "frequency",
            "schedule",
            "start_date",
            "end_date",
            "is_active",
            "last_reminded_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
