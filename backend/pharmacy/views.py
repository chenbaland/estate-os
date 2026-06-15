from core.viewsets import TenantViewSet
from pharmacy.models import DrugReminder, MedicationOrder, Prescription
from pharmacy.serializers import (
    DrugReminderSerializer,
    MedicationOrderSerializer,
    PrescriptionSerializer,
)


class PrescriptionViewSet(TenantViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    filterset_fields = ["resident", "status"]
    search_fields = ["prescription_number", "doctor_name", "hospital_name"]


class MedicationOrderViewSet(TenantViewSet):
    queryset = MedicationOrder.objects.all()
    serializer_class = MedicationOrderSerializer
    filterset_fields = ["prescription", "resident", "status", "delivery_type"]
    search_fields = ["order_number", "payment_reference"]


class DrugReminderViewSet(TenantViewSet):
    queryset = DrugReminder.objects.all()
    serializer_class = DrugReminderSerializer
    filterset_fields = ["resident", "frequency", "is_active"]
    search_fields = ["medication_name", "dosage"]
