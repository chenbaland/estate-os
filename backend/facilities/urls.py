from rest_framework.routers import DefaultRouter

from facilities.views import BlackoutDateViewSet, BookingViewSet, FacilityViewSet

router = DefaultRouter()
router.register(r"facilities", FacilityViewSet, basename="facility")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"blackout-dates", BlackoutDateViewSet, basename="blackout-date")

urlpatterns = router.urls
