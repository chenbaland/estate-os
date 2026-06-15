from rest_framework.routers import DefaultRouter

from billing.views import DebtRecordViewSet, FeeTypeViewSet, InvoiceViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"fee-types", FeeTypeViewSet, basename="fee-type")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"debts", DebtRecordViewSet, basename="debt-record")

urlpatterns = router.urls
