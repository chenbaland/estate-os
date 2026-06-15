from rest_framework.routers import DefaultRouter

from healthcare.views import (
    AmbulanceRequestViewSet,
    AppointmentViewSet,
    HospitalViewSet,
    MedicalRecordViewSet,
)

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet, basename="hospital")
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"ambulance-requests", AmbulanceRequestViewSet, basename="ambulance-request")
router.register(r"medical-records", MedicalRecordViewSet, basename="medical-record")

urlpatterns = router.urls
