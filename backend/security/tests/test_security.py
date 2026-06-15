"""Tests for the security module."""
import pytest
from rest_framework.test import APIClient

from accounts.models import User
from estates.models import Estate, Unit
from residents.models import ResidentProfile
from security.models import EmergencyBroadcast, Incident, PatrolLog, SOSAlert


@pytest.fixture
def estate(db):
    return Estate.objects.create(name="Security Estate", slug="security-estate", total_units=5, is_active=True)


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(email="secadmin@test.com", username="secadmin", password="adminpass123!")


@pytest.fixture
def resident_user(db):
    return User.objects.create_user(email="secresident@test.com", username="secresident", password="respass123!")


@pytest.fixture
def unit(db, estate):
    return Unit.objects.create(estate=estate, unit_number="S1", unit_type="apartment", is_active=True)


@pytest.fixture
def resident_profile(db, resident_user, estate, unit):
    return ResidentProfile.objects.create(
        user=resident_user, estate=estate, unit=unit,
        resident_type=ResidentProfile.ResidentType.OWNER, status=ResidentProfile.Status.ACTIVE,
    )


@pytest.fixture
def auth_client(admin_user, estate):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    client.credentials(HTTP_X_ESTATE_ID=str(estate.id))
    return client


@pytest.mark.django_db
class TestIncident:
    def test_create_incident(self, auth_client, admin_user):
        response = auth_client.post(
            "/api/v1/security/incidents/",
            data={
                "title": "Break-in attempt",
                "description": "Someone tried to break into Unit A1",
                "category": "theft",
                "severity": "high",
                "location": "Main Gate",
                "reported_by": str(admin_user.id),
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Break-in attempt"

    def test_list_incidents(self, auth_client, estate, admin_user):
        Incident.objects.create(
            estate=estate, title="Test Incident", category="theft", severity="low",
            status="open", reported_by=admin_user,
        )
        response = auth_client.get("/api/v1/security/incidents/")
        assert response.status_code == 200
        assert len(response.json()["results"]) >= 1

    def test_filter_incidents_by_severity(self, auth_client, estate, admin_user):
        Incident.objects.create(estate=estate, title="High Severity", category="theft", severity="high", status="open", reported_by=admin_user)
        Incident.objects.create(estate=estate, title="Low Severity", category="noise", severity="low", status="open", reported_by=admin_user)
        response = auth_client.get("/api/v1/security/incidents/?severity=high")
        assert response.status_code == 200
        for item in response.json()["results"]:
            assert item["severity"] == "high"


@pytest.mark.django_db
class TestSOSAlert:
    def test_create_sos_alert(self, auth_client, resident_profile):
        response = auth_client.post(
            "/api/v1/security/sos-alerts/",
            data={"resident": str(resident_profile.id), "message": "Emergency!"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["status"] == "active"

    def test_acknowledge_sos_alert(self, auth_client, estate, resident_profile):
        alert = SOSAlert.objects.create(estate=estate, resident=resident_profile, status=SOSAlert.Status.ACTIVE)
        response = auth_client.post(f"/api/v1/security/sos-alerts/{alert.id}/acknowledge/", format="json")
        assert response.status_code == 200
        alert.refresh_from_db()
        assert alert.status == SOSAlert.Status.ACKNOWLEDGED
        assert alert.acknowledged_by is not None

    def test_resolve_sos_alert(self, auth_client, estate, resident_profile):
        alert = SOSAlert.objects.create(estate=estate, resident=resident_profile, status=SOSAlert.Status.ACKNOWLEDGED)
        response = auth_client.post(
            f"/api/v1/security/sos-alerts/{alert.id}/resolve/",
            data={"response_notes": "Officers arrived and situation resolved"},
            format="json",
        )
        assert response.status_code == 200
        alert.refresh_from_db()
        assert alert.status == SOSAlert.Status.RESOLVED
        assert alert.resolved_at is not None


@pytest.mark.django_db
class TestEmergencyBroadcast:
    def test_create_emergency_broadcast(self, auth_client):
        response = auth_client.post(
            "/api/v1/security/emergency-broadcasts/",
            data={"title": "Gate Malfunction", "message": "Main gate is temporarily closed", "priority": "urgent", "channel": "all"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Gate Malfunction"

    def test_broadcast_sent_by_is_current_user(self, auth_client, admin_user):
        response = auth_client.post(
            "/api/v1/security/emergency-broadcasts/",
            data={"title": "Test", "message": "Test broadcast", "priority": "info", "channel": "sms"},
            format="json",
        )
        assert response.status_code == 201
        broadcast = EmergencyBroadcast.objects.get(id=response.json()["id"])
        assert broadcast.sent_by == admin_user
