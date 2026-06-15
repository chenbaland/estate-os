from rest_framework.routers import DefaultRouter

from utilities.views import (
    ConsumptionRecordViewSet,
    UtilityAccountViewSet,
    UtilityTransactionViewSet,
)

router = DefaultRouter()
router.register(r"accounts", UtilityAccountViewSet, basename="utility-account")
router.register(r"transactions", UtilityTransactionViewSet, basename="utility-transaction")
router.register(r"consumption", ConsumptionRecordViewSet, basename="consumption-record")

urlpatterns = router.urls
