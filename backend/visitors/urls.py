from rest_framework.routers import DefaultRouter

from visitors.views import BlacklistViewSet, VisitorLogViewSet, VisitorPassViewSet

router = DefaultRouter()
router.register(r"passes", VisitorPassViewSet, basename="visitor-pass")
router.register(r"logs", VisitorLogViewSet, basename="visitor-log")
router.register(r"blacklist", BlacklistViewSet, basename="blacklist")

urlpatterns = router.urls
