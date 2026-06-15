from rest_framework.routers import DefaultRouter

from maintenance.views import SLAConfigViewSet, TicketCommentViewSet, TicketViewSet

router = DefaultRouter()
router.register(r"sla-configs", SLAConfigViewSet, basename="sla-config")
router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"ticket-comments", TicketCommentViewSet, basename="ticket-comment")

urlpatterns = router.urls
