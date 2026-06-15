from rest_framework.routers import DefaultRouter

from residents.views import (
    DomesticStaffViewSet,
    FamilyMemberViewSet,
    ResidentProfileViewSet,
    VehicleViewSet,
)

router = DefaultRouter()
router.register(r"profiles", ResidentProfileViewSet, basename="resident-profile")
router.register(r"family-members", FamilyMemberViewSet, basename="family-member")
router.register(r"domestic-staff", DomesticStaffViewSet, basename="domestic-staff")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = router.urls
