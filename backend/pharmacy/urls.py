from rest_framework.routers import DefaultRouter

from pharmacy.views import DrugReminderViewSet, MedicationOrderViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r"prescriptions", PrescriptionViewSet, basename="prescription")
router.register(r"medication-orders", MedicationOrderViewSet, basename="medication-order")
router.register(r"drug-reminders", DrugReminderViewSet, basename="drug-reminder")

urlpatterns = router.urls
