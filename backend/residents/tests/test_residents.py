"""Resident onboarding, family, and vehicle tests."""
import pytest
from django.utils import timezone

from residents.models import DomesticStaff, FamilyMember, ResidentProfile, Vehicle


@pytest.mark.django_db
class TestResidentOnboarding:
    def test_create_pending_resident(self, user, estate, unit):
        profile = ResidentProfile.objects.create(
            estate=estate,
            user=user,
            unit=unit,
            resident_type=ResidentProfile.ResidentType.TENANT,
            status=ResidentProfile.Status.PENDING,
        )
        assert profile.status == ResidentProfile.Status.PENDING
        assert profile.is_primary is False

    def test_activate_resident_on_move_in(self, resident):
        resident.status = ResidentProfile.Status.ACTIVE
        resident.move_in_date = timezone.now().date()
        resident.save()
        resident.refresh_from_db()
        assert resident.status == ResidentProfile.Status.ACTIVE
        assert resident.move_in_date is not None

    def test_primary_resident_per_unit(self, resident, user, estate, unit):
        second_user = type(user).objects.create_user(
            username="resident2",
            email="resident2@test.estateos",
            password="testpass12345",
        )
        spouse = ResidentProfile.objects.create(
            estate=estate,
            user=second_user,
            unit=unit,
            resident_type=ResidentProfile.ResidentType.FAMILY,
            status=ResidentProfile.Status.ACTIVE,
            is_primary=False,
        )
        assert resident.is_primary is True
        assert spouse.is_primary is False

    def test_resident_soft_delete(self, resident):
        resident.soft_delete()
        assert ResidentProfile.objects.filter(id=resident.id).count() == 0


@pytest.mark.django_db
class TestFamilyMembers:
    def test_add_family_member(self, family_member, resident):
        assert family_member.primary_resident_id == resident.id
        assert family_member.relationship == FamilyMember.Relationship.CHILD
        assert family_member.has_gate_access is True

    def test_family_member_gate_access_expiry(self, resident):
        member = FamilyMember.objects.create(
            estate=resident.estate,
            primary_resident=resident,
            full_name="Guest Relative",
            relationship=FamilyMember.Relationship.OTHER,
            has_gate_access=True,
            access_expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        assert member.access_expires_at > timezone.now()

    def test_deactivate_family_member(self, family_member):
        family_member.is_active = False
        family_member.save()
        family_member.refresh_from_db()
        assert family_member.is_active is False


@pytest.mark.django_db
class TestVehicles:
    def test_register_vehicle(self, vehicle, resident):
        assert vehicle.license_plate == "LAG-123-XY"
        assert vehicle.owner_id == resident.id

    def test_unique_license_plate_per_estate(self, resident, vehicle):
        with pytest.raises(Exception):
            Vehicle.objects.create(
                estate=resident.estate,
                owner=resident,
                license_plate=vehicle.license_plate,
            )

    def test_ev_vehicle_flag(self, resident):
        ev = Vehicle.objects.create(
            estate=resident.estate,
            owner=resident,
            vehicle_type=Vehicle.VehicleType.EV,
            license_plate="LAG-EV-001",
            is_ev=True,
        )
        assert ev.is_ev is True


@pytest.mark.django_db
class TestDomesticStaff:
    def test_register_domestic_staff(self, resident):
        staff = DomesticStaff.objects.create(
            estate=resident.estate,
            employer=resident,
            full_name="Grace Nwosu",
            role=DomesticStaff.StaffRole.CLEANER,
            phone="+2348022222222",
            has_gate_access=True,
        )
        assert staff.is_active is True
        assert staff.role == DomesticStaff.StaffRole.CLEANER
