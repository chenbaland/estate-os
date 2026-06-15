"""Marketplace vendor, product, and order tests."""
from decimal import Decimal

import pytest

from marketplace.models import Cart, Order, Product, Review, Vendor


@pytest.mark.django_db
class TestVendors:
    def test_create_vendor(self, vendor):
        assert vendor.status == Vendor.Status.ACTIVE
        assert vendor.business_name == "Fresh Mart"

    def test_vendor_pending_approval(self, estate, user):
        pending = Vendor.objects.create(
            estate=estate,
            user=user,
            business_name="New Shop",
            slug="new-shop",
            category="services",
            status=Vendor.Status.PENDING,
        )
        assert pending.status == Vendor.Status.PENDING

    def test_suspend_vendor(self, vendor):
        vendor.status = Vendor.Status.SUSPENDED
        vendor.save()
        vendor.refresh_from_db()
        assert vendor.status == Vendor.Status.SUSPENDED


@pytest.mark.django_db
class TestProducts:
    def test_create_product(self, product, vendor):
        assert product.vendor_id == vendor.id
        assert product.stock_quantity == 100

    def test_out_of_stock_status(self, product):
        product.stock_quantity = 0
        product.status = Product.Status.OUT_OF_STOCK
        product.save()
        product.refresh_from_db()
        assert product.status == Product.Status.OUT_OF_STOCK

    def test_featured_product(self, product):
        product.is_featured = True
        product.save()
        assert product.is_featured is True


@pytest.mark.django_db
class TestOrders:
    def test_create_order(self, marketplace_order):
        assert marketplace_order.status == Order.Status.PENDING
        assert marketplace_order.total_amount == Decimal("5500.00")

    def test_order_lifecycle(self, marketplace_order):
        marketplace_order.status = Order.Status.CONFIRMED
        marketplace_order.save()
        marketplace_order.status = Order.Status.PREPARING
        marketplace_order.save()
        marketplace_order.status = Order.Status.DELIVERED
        marketplace_order.save()
        marketplace_order.refresh_from_db()
        assert marketplace_order.status == Order.Status.DELIVERED

    def test_cancel_order(self, marketplace_order):
        marketplace_order.status = Order.Status.CANCELLED
        marketplace_order.save()
        assert marketplace_order.status == Order.Status.CANCELLED


@pytest.mark.django_db
class TestCartAndReviews:
    def test_shopping_cart(self, estate, user, vendor, product):
        cart = Cart.objects.create(
            estate=estate,
            user=user,
            vendor=vendor,
            items=[
                {
                    "product_id": str(product.id),
                    "quantity": 3,
                    "unit_price": str(product.price),
                }
            ],
            subtotal=Decimal("7500.00"),
        )
        assert cart.is_active is True

    def test_product_review(self, estate, user, vendor, product, marketplace_order):
        review = Review.objects.create(
            estate=estate,
            user=user,
            vendor=vendor,
            product=product,
            order=marketplace_order,
            rating=5,
            title="Great quality",
            comment="Fresh organic eggs",
            is_verified_purchase=True,
        )
        assert review.is_visible is True
        assert review.rating == 5
