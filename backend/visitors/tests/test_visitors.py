"""Tests for the visitors module."""
import uuid
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from estates.models import Estate, Unit
from residents.models import ResidentProfile
from visitors.models import Blacklist, VisitorLog, VisitorPass


@pytest.fixture
def estate(db):
    return Estate.objects.create(
        name="Test Estate V",
        slug="test-estate-v",
        total_units=10,
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="vadmin@estate.test",
        username="vadmin",
        password="adminpass123!",
    )


@pytest.fixture
def resident_user(db):
    return User.objects.create_user(
        email="vresident@estate.test",
        username="vresident",
        password="respass123!",
    )


@pytest.fixture
def unit(db, estate):
    return Unit.objects.create(estate=estate, unit_number="V1", unit_type="apartment", is_active=True)


@pytest.fixture
def resident_profile(db, resident_user, estate, unit):
    return ResidentProfile.objects.create(
        user=resident_user,
        estate=estate,
        unit=unit,
        resident_type=ResidentProfile.ResidentType.OWNER,
        status=ResidentProfile.Status.ACTIVE,
    )


@pytest.fixture
def auth_client(admin_user, estate):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    client.credentials(HTTP_X_ESTATE_ID=str(estate.id))
    return client


def make_pass(estate, resident_profile, phone="+2348000000001", name="John Doe", status=VisitorPass.Status.ACTIVE, hours_ahead=23, max_entries=1):
    return VisitorPass.objects.create(
        estate=estate,
        host=resident_profile,
        visitor_name=name,
        visitor_phone=phone,
        pass_type=VisitorPass.PassType.SINGLE,
        status=status,
        valid_from=timezone.now() - timedelta(hours=1),
        valid_until=timezone.now() + timedelta(hours=hours_ahead),
        qr_code=str(uuid.uuid4()),
        max_entries=max_entries,
    )


@pytest.mark.django_db
class TestVisitorPassCRUD:
    def test_list_passes(self, auth_client, estate, resident_profile):
        make_pass(estate, resident_profile)
        response = auth_client.get("/api/v1/visitors/passes/")
        assert response.status_code == 200
        assert len(response.json()["results"]) >= 1

    def test_create_visitor_pass(self, auth_client, resident_profile):
        response = auth_client.post(
            "/api/v1/visitors/passes/",
            data={
                "host": str(resident_profile.id),
                "visitor_name": "Jane Smith",
                "visitor_phone": "+2348111111111",
                "pass_type": "single",
                "valid_from": (timezone.now()).isoformat(),
                "valid_until": (timezone.now() + timedelta(hours=12)).isoformat(),
                "max_entries": 1,
            },
            format="json",
        )
        assert response.status_code == 201

    def test_scan_valid_pass(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile)
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry", "gate_name": "Gate 1"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "log_id" in data

    def test_scan_expired_pass(self, auth_client, estate, resident_profile):
        expired = make_pass(estate, resident_profile, hours_ahead=-1)
        expired.valid_until = timezone.now() - timedelta(hours=1)
        expired.save()
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": expired.qr_code, "direction": "entry"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["valid"] is False

    def test_scan_invalid_qr_code(self, auth_client):
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": "nonexistent-qr-code-xyz", "direction": "entry"},
            format="json",
        )
        assert response.status_code == 404

    def test_scan_increments_entry_count(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile, max_entries=5)
        before = vp.entries_used
        auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry"},
            format="json",
        )
        vp.refresh_from_db()
        assert vp.entries_used == before + 1

    def test_scan_exhausted_pass_marked_used(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile, max_entries=1)
        auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry"},
            format="json",
        )
        vp.refresh_from_db()
        assert vp.status == VisitorPass.Status.USED

    def test_scan_blacklisted_by_phone_denied(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile, phone="+2348999999999")
        Blacklist.objects.create(
            estate=estate,
            phone="+2348999999999",
            full_name="Blacklisted Person",
            reason="security",
            description="Security risk",
        )
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry"},
            format="json",
        )
        assert response.status_code == 403
        assert response.json()["valid"] is False

    def test_scan_blacklisted_by_name_denied(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile, name="Wanted Criminal", phone="")
        Blacklist.objects.create(
            estate=estate,
            full_name="Wanted Criminal",
            reason="security",
            description="Assault history",
        )
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry"},
            format="json",
        )
        assert response.status_code == 403

    def test_scan_creates_visitor_log(self, auth_client, estate, resident_profile):
        vp = make_pass(estate, resident_profile)
        before_count = VisitorLog.objects.count()
        auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": vp.qr_code, "direction": "entry"},
            format="json",
        )
        assert VisitorLog.objects.count() == before_count + 1

    def test_scan_revoked_pass_rejected(self, auth_client, estate, resident_profile):
        revoked = make_pass(estate, resident_profile, status=VisitorPass.Status.REVOKED)
        response = auth_client.post(
            "/api/v1/visitors/passes/scan/",
            data={"qr_code": revoked.qr_code, "direction": "entry"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["valid"] is False


@pytest.mark.django_db
class TestBlacklist:
    def test_create_blacklist_entry(self, auth_client):
        response = auth_client.post(
            "/api/v1/visitors/blacklist/",
            data={"full_name": "Bad Actor", "phone": "+2340000000099", "reason": "security", "description": "Theft incident"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["full_name"] == "Bad Actor"

    def test_list_blacklist(self, auth_client, estate):
        Blacklist.objects.create(estate=estate, full_name="X", phone="+1999", reason="other", description="test")
        response = auth_client.get("/api/v1/visitors/blacklist/")
        assert response.status_code == 200
        assert len(response.json()["results"]) >= 1

    def test_deactivate_blacklist_entry(self, auth_client, estate):
        entry = Blacklist.objects.create(estate=estate, full_name="Y", phone="+1888", reason="other", description="test")
        response = auth_client.patch(
            f"/api/v1/visitors/blacklist/{entry.id}/",
            data={"is_active": False},
            format="json",
        )
        assert response.status_code == 200
        entry.refresh_from_db()
        assert entry.is_active is False
