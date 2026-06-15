from core.serializers import TenantModelSerializer
from marketplace.models import Cart, Order, Product, Review, Vendor


class VendorSerializer(TenantModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "estate",
            "user",
            "business_name",
            "slug",
            "description",
            "logo",
            "cover_image",
            "category",
            "phone",
            "email",
            "address",
            "status",
            "rating_avg",
            "rating_count",
            "commission_rate",
            "operating_hours",
            "is_verified",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "rating_avg", "rating_count", "created_at", "updated_at"]


class ProductSerializer(TenantModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "estate",
            "vendor",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "compare_at_price",
            "currency",
            "sku",
            "stock_quantity",
            "status",
            "images",
            "attributes",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class CartSerializer(TenantModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "estate",
            "user",
            "vendor",
            "items",
            "subtotal",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class OrderSerializer(TenantModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "estate",
            "order_number",
            "user",
            "vendor",
            "status",
            "items",
            "subtotal",
            "delivery_fee",
            "total_amount",
            "currency",
            "delivery_address",
            "unit",
            "payment_reference",
            "notes",
            "delivered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class ReviewSerializer(TenantModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "estate",
            "user",
            "vendor",
            "product",
            "order",
            "rating",
            "title",
            "comment",
            "is_verified_purchase",
            "is_visible",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
