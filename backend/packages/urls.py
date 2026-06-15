from rest_framework.routers import DefaultRouter

from packages.views import PackageLogViewSet, PackageViewSet

router = DefaultRouter()
router.register(r"packages", PackageViewSet, basename="package")
router.register(r"logs", PackageLogViewSet, basename="package-log")

urlpatterns = router.urls
