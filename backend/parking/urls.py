from rest_framework.routers import DefaultRouter

from parking.views import EVChargingSessionViewSet, ParkingPermitViewSet, ParkingSlotViewSet

router = DefaultRouter()
router.register(r"slots", ParkingSlotViewSet, basename="parking-slot")
router.register(r"permits", ParkingPermitViewSet, basename="parking-permit")
router.register(r"ev-sessions", EVChargingSessionViewSet, basename="ev-charging-session")

urlpatterns = router.urls
