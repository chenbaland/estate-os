from core.serializers import TenantModelSerializer
from community.models import Announcement, Comment, Group, LostFound, Message, Poll, Post


class PostSerializer(TenantModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "estate",
            "author",
            "title",
            "body",
            "status",
            "category",
            "attachments",
            "like_count",
            "comment_count",
            "is_pinned",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "like_count", "comment_count", "created_at", "updated_at"]


class CommentSerializer(TenantModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "estate",
            "post",
            "author",
            "parent",
            "body",
            "like_count",
            "is_hidden",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "like_count", "created_at", "updated_at"]


class PollSerializer(TenantModelSerializer):
    class Meta:
        model = Poll
        fields = [
            "id",
            "estate",
            "created_by",
            "question",
            "options",
            "status",
            "allow_multiple",
            "is_anonymous",
            "closes_at",
            "vote_count",
            "results",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "vote_count", "results", "created_at", "updated_at"]


class AnnouncementSerializer(TenantModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "estate",
            "title",
            "body",
            "priority",
            "published_by",
            "published_at",
            "expires_at",
            "is_pinned",
            "target_audience",
            "attachments",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class LostFoundSerializer(TenantModelSerializer):
    class Meta:
        model = LostFound
        fields = [
            "id",
            "estate",
            "reported_by",
            "item_type",
            "status",
            "title",
            "description",
            "location",
            "found_date",
            "photo",
            "contact_info",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class GroupSerializer(TenantModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "estate",
            "name",
            "slug",
            "description",
            "created_by",
            "visibility",
            "cover_image",
            "member_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "member_count", "created_at", "updated_at"]


class MessageSerializer(TenantModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "estate",
            "sender",
            "recipient",
            "group",
            "body",
            "attachments",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
