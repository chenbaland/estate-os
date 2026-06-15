from rest_framework.routers import DefaultRouter

from ai.views import ConversationViewSet, DocumentViewSet, PredictionViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"predictions", PredictionViewSet, basename="prediction")

urlpatterns = router.urls
