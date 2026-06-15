from rest_framework.routers import DefaultRouter

from marketplace.views import (
    CartViewSet,
    OrderViewSet,
    ProductViewSet,
    ReviewViewSet,
    VendorViewSet,
)

router = DefaultRouter()
router.register(r"vendors", VendorViewSet, basename="vendor")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"carts", CartViewSet, basename="cart")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = router.urls
