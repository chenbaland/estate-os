from rest_framework.routers import DefaultRouter

from community.views import (
    AnnouncementViewSet,
    CommentViewSet,
    GroupViewSet,
    LostFoundViewSet,
    MessageViewSet,
    PollViewSet,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"polls", PollViewSet, basename="poll")
router.register(r"announcements", AnnouncementViewSet, basename="announcement")
router.register(r"lost-found", LostFoundViewSet, basename="lost-found")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = router.urls
