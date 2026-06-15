"""Audit logging tests."""
import logging
from unittest.mock import patch

import pytest

from core.audit import AuditEvent, record_audit_event


@pytest.mark.django_db
class TestAuditLogging:
    def test_record_audit_event_returns_structured_event(self, user, estate):
        event = record_audit_event(
            action="role.assign",
            resource_type="accounts.user_role",
            resource_id="role-uuid-123",
            actor=user,
            estate=estate,
            before_state=None,
            after_state={"role": "resident"},
            ip_address="192.168.1.1",
            user_agent="pytest",
        )
        assert isinstance(event, AuditEvent)
        assert event.action == "role.assign"
        assert event.actor_id == str(user.id)
        assert event.estate_id == str(estate.id)
        assert event.after_state["role"] == "resident"

    def test_audit_event_logged(self, user, estate):
        with patch.object(logging.getLogger("estateos.audit"), "info") as mock_info:
            record_audit_event(
                action="blacklist.add",
                resource_type="visitors.blacklist",
                actor=user,
                estate=estate,
                after_state={"full_name": "Banned Person"},
            )
        mock_info.assert_called_once()
        assert mock_info.call_args[0][0] == "audit_event"
        assert mock_info.call_args[1]["extra"]["audit"]["action"] == "blacklist.add"

    def test_audit_trace_id_unique(self, user, estate):
        event_a = record_audit_event(
            action="invoice.write_off",
            resource_type="billing.invoice",
            actor=user,
            estate=estate,
        )
        event_b = record_audit_event(
            action="invoice.write_off",
            resource_type="billing.invoice",
            actor=user,
            estate=estate,
        )
        assert event_a.trace_id != event_b.trace_id

    def test_audit_without_actor(self, estate):
        event = record_audit_event(
            action="system.cleanup",
            resource_type="core.task",
            estate=estate,
        )
        assert event.actor_id is None
