"""Immutable audit logging for EstateOS."""
import logging
import uuid
from dataclasses import asdict, dataclass, field
from typing import Optional

logger = logging.getLogger("estateos.audit")


@dataclass
class AuditEvent:
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    actor_id: Optional[str] = None
    estate_id: Optional[str] = None
    before_state: Optional[dict] = None
    after_state: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)


def record_audit_event(
    *,
    action: str,
    resource_type: str,
    resource_id=None,
    actor=None,
    estate=None,
    before_state=None,
    after_state=None,
    ip_address=None,
    user_agent=None,
    trace_id=None,
) -> AuditEvent:
    """Record an immutable audit event via structured logging."""
    estate_id = None
    if estate is not None:
        estate_id = str(getattr(estate, "id", estate))

    event = AuditEvent(
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        actor_id=str(actor.id) if actor else None,
        estate_id=estate_id,
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
        trace_id=trace_id or uuid.uuid4().hex,
    )
    logger.info("audit_event", extra={"audit": asdict(event)})
    return event
