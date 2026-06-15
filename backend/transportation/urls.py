from rest_framework.routers import DefaultRouter

from transportation.views import RideRequestViewSet

router = DefaultRouter()
router.register(r"ride-requests", RideRequestViewSet, basename="ride-request")

urlpatterns = router.urls
