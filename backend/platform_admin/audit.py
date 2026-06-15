"""Persisted audit trail for platform super-admin actions."""
from typing import Optional

from django.http import HttpRequest

from core.audit import record_audit_event
from platform_admin.models import PlatformAuditLog


def _client_meta(request: HttpRequest) -> tuple[Optional[str], str]:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else None
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return ip_address, user_agent


def record_platform_audit(
    *,
    request: HttpRequest,
    action: str,
    resource_type: str,
    summary: str,
    resource_id=None,
    estate=None,
    metadata=None,
    before_state=None,
    after_state=None,
) -> PlatformAuditLog:
    actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    ip_address, user_agent = _client_meta(request)

    event = record_audit_event(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor=actor,
        estate=estate,
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return PlatformAuditLog.objects.create(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor=actor,
        estate=estate,
        summary=summary,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent,
        trace_id=event.trace_id,
    )
