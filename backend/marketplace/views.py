from core.viewsets import TenantViewSet
from marketplace.models import Cart, Order, Product, Review, Vendor
from marketplace.serializers import (
    CartSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
    VendorSerializer,
)


class VendorViewSet(TenantViewSet):
    queryset = Vendor.objects.select_related("user")
    serializer_class = VendorSerializer
    filterset_fields = ["user", "category", "status", "is_verified"]
    search_fields = ["business_name", "slug", "phone", "email"]


class ProductViewSet(TenantViewSet):
    queryset = Product.objects.select_related("vendor")
    serializer_class = ProductSerializer
    filterset_fields = ["vendor", "category", "status", "is_featured"]
    search_fields = ["name", "slug", "sku", "description"]


class CartViewSet(TenantViewSet):
    queryset = Cart.objects.select_related("user", "vendor").prefetch_related("items__product")
    serializer_class = CartSerializer
    filterset_fields = ["user", "vendor", "is_active"]


class OrderViewSet(TenantViewSet):
    queryset = Order.objects.select_related("user", "vendor", "unit").prefetch_related("items__product")
    serializer_class = OrderSerializer
    filterset_fields = ["user", "vendor", "status", "unit"]
    search_fields = ["order_number", "payment_reference", "delivery_address"]


class ReviewViewSet(TenantViewSet):
    queryset = Review.objects.select_related("user", "vendor", "product")
    serializer_class = ReviewSerializer
    filterset_fields = ["user", "vendor", "product", "rating", "is_visible"]
    search_fields = ["title", "comment"]
