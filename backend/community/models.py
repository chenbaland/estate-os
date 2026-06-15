from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Post(TenantBaseModel):
    """Community forum post."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        FLAGGED = "flagged", "Flagged"

    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED, db_index=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    attachments = models.JSONField(default=list, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "community_post"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["author", "status"]),
            models.Index(fields=["is_pinned", "created_at"]),
        ]


class Comment(TenantBaseModel):
    """Comment on a community post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="community_comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    body = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "community_comment"
        indexes = [
            models.Index(fields=["estate", "post", "created_at"]),
            models.Index(fields=["author"]),
        ]


class Poll(TenantBaseModel):
    """Community poll."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    created_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=500)
    options = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    allow_multiple = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    closes_at = models.DateTimeField(null=True, blank=True, db_index=True)
    vote_count = models.PositiveIntegerField(default=0)
    results = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "community_poll"
        indexes = [
            models.Index(fields=["estate", "status", "closes_at"]),
        ]


class Announcement(TenantBaseModel):
    """Official estate announcement."""

    class Priority(models.TextChoices):
        NORMAL = "normal", "Normal"
        IMPORTANT = "important", "Important"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=255)
    body = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL, db_index=True)
    published_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False, db_index=True)
    target_audience = models.JSONField(default=dict, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "community_announcement"
        indexes = [
            models.Index(fields=["estate", "is_active", "published_at"]),
            models.Index(fields=["priority", "is_pinned"]),
        ]


class LostFound(TenantBaseModel):
    """Lost and found item listing."""

    class ItemType(models.TextChoices):
        LOST = "lost", "Lost"
        FOUND = "found", "Found"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLAIMED = "claimed", "Claimed"
        CLOSED = "closed", "Closed"

    reported_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="lost_found_items")
    item_type = models.CharField(max_length=10, choices=ItemType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    found_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="community/lostfound/%Y/%m/", blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "community_lost_found"
        indexes = [
            models.Index(fields=["estate", "item_type", "status"]),
        ]


class Group(TenantBaseModel):
    """Community interest group."""

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        INVITE_ONLY = "invite_only", "Invite Only"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="created_groups")
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    cover_image = models.ImageField(upload_to="community/groups/%Y/%m/", blank=True, null=True)
    member_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "community_group"
        unique_together = [("estate", "slug")]
        indexes = [
            models.Index(fields=["estate", "visibility", "is_active"]),
        ]


class Message(TenantBaseModel):
    """Direct or group message."""

    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_messages",
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="messages")
    body = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "community_message"
        indexes = [
            models.Index(fields=["estate", "recipient", "is_read"]),
            models.Index(fields=["group", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]
