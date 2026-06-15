from core.viewsets import TenantViewSet
from community.models import Announcement, Comment, Group, LostFound, Message, Poll, Post
from community.serializers import (
    AnnouncementSerializer,
    CommentSerializer,
    GroupSerializer,
    LostFoundSerializer,
    MessageSerializer,
    PollSerializer,
    PostSerializer,
)


class PostViewSet(TenantViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    filterset_fields = ["author", "status", "category", "is_pinned"]
    search_fields = ["title", "body"]


class CommentViewSet(TenantViewSet):
    queryset = Comment.objects.select_related("post", "author", "parent")
    serializer_class = CommentSerializer
    filterset_fields = ["post", "author", "parent", "is_hidden"]
    search_fields = ["body"]


class PollViewSet(TenantViewSet):
    queryset = Poll.objects.select_related("created_by").prefetch_related("options")
    serializer_class = PollSerializer
    filterset_fields = ["created_by", "status", "allow_multiple"]
    search_fields = ["question"]


class AnnouncementViewSet(TenantViewSet):
    queryset = Announcement.objects.select_related("published_by")
    serializer_class = AnnouncementSerializer
    filterset_fields = ["priority", "is_pinned", "is_active", "published_by"]
    search_fields = ["title", "body"]


class LostFoundViewSet(TenantViewSet):
    queryset = LostFound.objects.select_related("reported_by")
    serializer_class = LostFoundSerializer
    filterset_fields = ["reported_by", "item_type", "status"]
    search_fields = ["title", "description", "location"]


class GroupViewSet(TenantViewSet):
    queryset = Group.objects.select_related("created_by")
    serializer_class = GroupSerializer
    filterset_fields = ["created_by", "visibility", "is_active"]
    search_fields = ["name", "slug", "description"]


class MessageViewSet(TenantViewSet):
    queryset = Message.objects.select_related("sender", "recipient", "group")
    serializer_class = MessageSerializer
    filterset_fields = ["sender", "recipient", "group", "is_read"]
    search_fields = ["body"]
