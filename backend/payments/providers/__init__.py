from payments.providers.base import BasePaymentProvider
from payments.providers.flutterwave import FlutterwaveProvider
from payments.providers.paystack import PaystackProvider
from payments.providers.stripe import StripeProvider

PROVIDER_REGISTRY = {
    "paystack": PaystackProvider,
    "flutterwave": FlutterwaveProvider,
    "stripe": StripeProvider,
}


def get_payment_provider(provider_name: str, **kwargs) -> BasePaymentProvider:
    """Factory function to instantiate a payment provider."""
    provider_class = PROVIDER_REGISTRY.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown payment provider: {provider_name}")
    return provider_class(**kwargs)
