from django.urls import path
from rest_framework.routers import DefaultRouter

from payments.views import (
    FlutterwaveWebhookView,
    PaymentProviderConfigViewSet,
    PaymentTransactionViewSet,
    PaystackWebhookView,
    StripeWebhookView,
)

router = DefaultRouter()
router.register(r"provider-configs", PaymentProviderConfigViewSet, basename="payment-provider-config")
router.register(r"transactions", PaymentTransactionViewSet, basename="payment-transaction")

urlpatterns = [
    path("webhooks/paystack/", PaystackWebhookView.as_view(), name="paystack-webhook"),
    path("webhooks/flutterwave/", FlutterwaveWebhookView.as_view(), name="flutterwave-webhook"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    *router.urls,
]
