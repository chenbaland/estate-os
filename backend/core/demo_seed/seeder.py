"""Idempotent demo / QA dataset for EstateOS dashboards and end-to-end testing."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from accounts.models import Permission, Role, UserRole
from ai.models import Conversation, Document, Prediction
from analytics.models import DashboardWidget, MetricSnapshot
from billing.models import DebtRecord, FeeType, Invoice, InvoiceLine, Payment
from community.models import Announcement, Comment, LostFound, Poll, Post
from core.demo_seed.constants import (
    DEMO_EMAIL_DOMAIN,
    DEMO_ESTATE_SLUGS,
    DEMO_MARKER,
    DEMO_PASSWORD,
    DEMO_PERMISSIONS,
    DEMO_SUPERUSER,
    OAK_HEIGHTS,
    OAK_HEIGHTS_SLUG,
    PALM_GROVE,
    PALM_GROVE_SLUG,
    ROLE_PERMISSION_CODES,
)
from estates.models import Block, Estate, Unit
from facilities.models import Booking, Facility
from maintenance.models import SLAConfig, Ticket
from marketplace.models import Order, Product, Vendor
from notifications.models import Notification, NotificationTemplate
from packages.models import Package, PackageLog
from parking.models import ParkingPermit, ParkingSlot
from payments.models import PaymentProviderConfig
from pharmacy.models import MedicationOrder, Prescription
from platform_admin.models import PlatformAuditLog
from platform_admin.services import create_estate, seed_estate_roles
from residents.models import FamilyMember, ResidentProfile, Vehicle
from security.models import EmergencyBroadcast, Incident, PatrolLog, SOSAlert
from transportation.models import RideRequest
from utilities.models import UtilityAccount, UtilityTransaction
from visitors.models import Blacklist, VisitorLog, VisitorPass
from healthcare.models import Appointment, Hospital

User = get_user_model()

MINIMAL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)


@dataclass
class SeedSummary:
    created: dict[str, int] = field(default_factory=dict)
    skipped: dict[str, int] = field(default_factory=dict)

    def bump(self, key: str, *, created: bool) -> None:
        bucket = self.created if created else self.skipped
        bucket[key] = bucket.get(key, 0) + 1


@dataclass
class EstateContext:
    estate: Estate
    blocks: dict[str, Block] = field(default_factory=dict)
    units: dict[str, Unit] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)
    users: dict[str, User] = field(default_factory=dict)
    residents: dict[str, ResidentProfile] = field(default_factory=dict)


class DemoSeeder:
    """Populate realistic cross-module data for QA and demo environments."""

    def __init__(self, *, flush: bool = False, verbosity: int = 1) -> None:
        self.flush = flush
        self.verbosity = verbosity
        self.summary = SeedSummary()
        self.superuser: User | None = None
        self.permissions: dict[str, Permission] = {}
        self.contexts: dict[str, EstateContext] = {}

    def run(self) -> SeedSummary:
        if self.flush:
            self._flush_demo_data()
        with transaction.atomic():
            self._seed_superuser()
            self._seed_permissions()
            self._seed_estates()
            self._seed_platform_audit()
            self._seed_palm_grove()
            self._seed_oak_heights()
        return self.summary

    def _log(self, message: str) -> None:
        if self.verbosity >= 1:
            print(message)

    def _flush_demo_data(self) -> None:
        self._log("Flushing existing demo data…")
        PlatformAuditLog.objects.filter(estate__slug__in=DEMO_ESTATE_SLUGS).delete()
        for slug in DEMO_ESTATE_SLUGS:
            Estate.all_objects.filter(slug=slug).delete()
        User.objects.filter(email__iendswith=f"@{DEMO_EMAIL_DOMAIN}").delete()
        Permission.objects.filter(code__in=[code for code, _, _ in DEMO_PERMISSIONS]).delete()

    def _seed_superuser(self) -> None:
        user, created = User.objects.get_or_create(
            email=DEMO_SUPERUSER["email"],
            defaults={
                "username": DEMO_SUPERUSER["username"],
                "first_name": DEMO_SUPERUSER["first_name"],
                "last_name": DEMO_SUPERUSER["last_name"],
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created or self.flush:
            user.set_password(DEMO_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["password", "is_staff", "is_superuser"])
        self.superuser = user
        self.summary.bump("superuser", created=created)

    def _seed_permissions(self) -> None:
        for code, name, module in DEMO_PERMISSIONS:
            perm, created = Permission.objects.get_or_create(
                code=code,
                defaults={"name": name, "module": module},
            )
            self.permissions[code] = perm
            self.summary.bump("permissions", created=created)

    def _seed_estates(self) -> None:
        for config in (PALM_GROVE, OAK_HEIGHTS):
            estate = Estate.objects.filter(slug=config["slug"]).first()
            created = estate is None
            if created:
                estate = create_estate({**config, "settings": {"demo_seed": DEMO_MARKER}})
            else:
                seed_estate_roles(estate)
            ctx = EstateContext(estate=estate)
            ctx.roles = {
                role.code: role
                for role in Role.objects.filter(estate=estate, is_active=True)
            }
            self._attach_role_permissions(ctx)
            self.contexts[config["slug"]] = ctx
            self.summary.bump("estates", created=created)

    def _attach_role_permissions(self, ctx: EstateContext) -> None:
        for role_code, perm_codes in ROLE_PERMISSION_CODES.items():
            role = ctx.roles.get(role_code)
            if role is None:
                continue
            perms = [self.permissions[c] for c in perm_codes if c in self.permissions]
            role.permissions.set(perms)

    def _seed_platform_audit(self) -> None:
        assert self.superuser is not None
        palm = self.contexts[PALM_GROVE_SLUG].estate
        oak = self.contexts[OAK_HEIGHTS_SLUG].estate
        entries = [
            (
                PlatformAuditLog.Action.ESTATE_CREATED,
                "estate",
                palm.id,
                palm,
                f"Created demo estate {palm.name}",
            ),
            (
                PlatformAuditLog.Action.ESTATE_CREATED,
                "estate",
                oak.id,
                oak,
                f"Created demo estate {oak.name}",
            ),
            (
                PlatformAuditLog.Action.ADMIN_ASSIGNED,
                "user_role",
                None,
                palm,
                "Assigned estate admin for Palm Grove Demo",
            ),
        ]
        for action, resource_type, resource_id, estate, summary in entries:
            _, created = PlatformAuditLog.objects.get_or_create(
                action=action,
                resource_type=resource_type,
                estate=estate,
                summary=summary,
                defaults={
                    "resource_id": resource_id,
                    "actor": self.superuser,
                    "metadata": {"demo_seed": DEMO_MARKER},
                    "ip_address": "127.0.0.1",
                    "user_agent": "seed_demo",
                },
            )
            self.summary.bump("platform_audit", created=created)

    def _seed_palm_grove(self) -> None:
        ctx = self.contexts[PALM_GROVE_SLUG]
        self._seed_structure(ctx, primary=True)
        self._seed_users(ctx, primary=True)
        self._seed_residents(ctx, primary=True)
        self._seed_billing(ctx)
        self._seed_visitors(ctx)
        self._seed_security(ctx)
        self._seed_maintenance(ctx)
        self._seed_facilities(ctx)
        self._seed_packages(ctx)
        self._seed_parking(ctx)
        self._seed_utilities(ctx)
        self._seed_marketplace(ctx)
        self._seed_community(ctx)
        self._seed_healthcare(ctx)
        self._seed_pharmacy(ctx)
        self._seed_transportation(ctx)
        self._seed_analytics(ctx)
        self._seed_notifications(ctx)
        self._seed_ai(ctx)
        self._sync_estate_counts(ctx)

    def _seed_oak_heights(self) -> None:
        ctx = self.contexts[OAK_HEIGHTS_SLUG]
        self._seed_structure(ctx, primary=False)
        self._seed_users(ctx, primary=False)
        self._seed_residents(ctx, primary=False)
        self._sync_estate_counts(ctx)

    def _seed_structure(self, ctx: EstateContext, *, primary: bool) -> None:
        if primary:
            block_specs = [
                ("Block A", "A", 4, 12),
                ("Block B", "B", 3, 8),
            ]
            unit_specs = [
                ("A", "A-101", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
                ("A", "A-102", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
                ("A", "A-103", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
                ("A", "A-104", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
                ("B", "B-201", Unit.UnitType.TOWNHOUSE, Unit.OccupancyStatus.VACANT),
                ("B", "B-202", Unit.UnitType.TOWNHOUSE, Unit.OccupancyStatus.VACANT),
            ]
        else:
            block_specs = [("Tower 1", "T1", 5, 4)]
            unit_specs = [
                ("T1", "T1-501", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
                ("T1", "T1-502", Unit.UnitType.APARTMENT, Unit.OccupancyStatus.VACANT),
            ]

        for name, code, floors, count in block_specs:
            block, created = Block.objects.get_or_create(
                estate=ctx.estate,
                code=code,
                defaults={
                    "name": name,
                    "floor_count": floors,
                    "unit_count": count,
                },
            )
            ctx.blocks[code] = block
            self.summary.bump("blocks", created=created)

        for block_code, unit_number, unit_type, occupancy in unit_specs:
            block = ctx.blocks[block_code]
            unit, created = Unit.objects.get_or_create(
                estate=ctx.estate,
                unit_number=unit_number,
                defaults={
                    "block": block,
                    "unit_type": unit_type,
                    "occupancy_status": occupancy,
                    "monthly_service_charge": Decimal("75000.00"),
                },
            )
            ctx.units[unit_number] = unit
            self.summary.bump("units", created=created)

    def _username_for_email(self, email: str) -> str:
        return email.replace("@", "_").replace(".", "_")[:150]

    def _user(
        self,
        ctx: EstateContext,
        *,
        key: str,
        email: str,
        first_name: str,
        last_name: str,
        role_code: str,
        is_staff: bool = False,
    ) -> User:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": self._username_for_email(email),
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": is_staff,
            },
        )
        if created or self.flush:
            user.set_password(DEMO_PASSWORD)
            user.is_staff = is_staff or user.is_staff
            user.save(update_fields=["password", "is_staff"])
        role = ctx.roles[role_code]
        _, role_created = UserRole.objects.update_or_create(
            user=user,
            role=role,
            estate=ctx.estate,
            defaults={"is_active": True, "assigned_by": self.superuser},
        )
        ctx.users[key] = user
        self.summary.bump("users", created=created)
        if role_created:
            self.summary.bump("user_roles", created=True)
        return user

    def _seed_users(self, ctx: EstateContext, *, primary: bool) -> None:
        slug = ctx.estate.slug.replace("-", "")
        if primary:
            specs = [
                ("admin", f"admin@{slug}.estateos", "Amaka", "Okafor", Role.RoleCode.ESTATE_ADMIN, True),
                ("finance", f"finance@{slug}.estateos", "Tunde", "Balogun", Role.RoleCode.FINANCE_ADMIN, True),
                ("security_admin", f"security-admin@{slug}.estateos", "Chidi", "Eze", Role.RoleCode.SECURITY_ADMIN, True),
                ("facility", f"facility@{slug}.estateos", "Funke", "Adeyemi", Role.RoleCode.FACILITY_ADMIN, True),
                ("resident1", f"resident1@{slug}.estateos", "Ada", "Okonkwo", Role.RoleCode.RESIDENT, False),
                ("resident2", f"resident2@{slug}.estateos", "Emeka", "Nwosu", Role.RoleCode.RESIDENT, False),
                ("tenant", f"tenant@{slug}.estateos", "Zainab", "Ibrahim", Role.RoleCode.RESIDENT, False),
                ("vendor", f"vendor@{slug}.estateos", "Kemi", "Mart", Role.RoleCode.VENDOR, False),
                ("technician", f"technician@{slug}.estateos", "Bola", "Ogun", Role.RoleCode.TECHNICIAN, False),
                ("security_staff", f"security-staff@{slug}.estateos", "Samuel", "Garba", Role.RoleCode.SECURITY_PERSONNEL, False),
            ]
        else:
            specs = [
                ("admin", f"admin@{slug}.estateos", "Ngozi", "Obi", Role.RoleCode.ESTATE_ADMIN, True),
                ("resident1", f"resident1@{slug}.estateos", "David", "Abubakar", Role.RoleCode.RESIDENT, False),
            ]
        for key, email, first, last, role_code, is_staff in specs:
            self._user(ctx, key=key, email=email, first_name=first, last_name=last, role_code=role_code, is_staff=is_staff)

    def _resident(
        self,
        ctx: EstateContext,
        *,
        key: str,
        user_key: str,
        unit_key: str,
        resident_type: str,
        status: str,
        is_primary: bool = True,
    ) -> ResidentProfile:
        user = ctx.users[user_key]
        unit = ctx.units[unit_key]
        profile, created = ResidentProfile.objects.get_or_create(
            estate=ctx.estate,
            user=user,
            defaults={
                "unit": unit,
                "resident_type": resident_type,
                "status": status,
                "is_primary": is_primary,
                "move_in_date": timezone.now().date() - timedelta(days=120),
            },
        )
        if status == ResidentProfile.Status.ACTIVE:
            unit.occupancy_status = Unit.OccupancyStatus.OCCUPIED
            if resident_type == ResidentProfile.ResidentType.OWNER:
                unit.owner = user
            unit.save(update_fields=["occupancy_status", "owner", "updated_at"])
        ctx.residents[key] = profile
        self.summary.bump("residents", created=created)
        return profile

    def _seed_residents(self, ctx: EstateContext, *, primary: bool) -> None:
        if primary:
            r1 = self._resident(
                ctx,
                key="owner",
                user_key="resident1",
                unit_key="A-101",
                resident_type=ResidentProfile.ResidentType.OWNER,
                status=ResidentProfile.Status.ACTIVE,
            )
            self._resident(
                ctx,
                key="pending",
                user_key="resident2",
                unit_key="A-102",
                resident_type=ResidentProfile.ResidentType.OWNER,
                status=ResidentProfile.Status.PENDING,
            )
            self._resident(
                ctx,
                key="tenant",
                user_key="tenant",
                unit_key="A-103",
                resident_type=ResidentProfile.ResidentType.TENANT,
                status=ResidentProfile.Status.ACTIVE,
                is_primary=True,
            )
            _, created = FamilyMember.objects.get_or_create(
                estate=ctx.estate,
                primary_resident=r1,
                full_name="Chidi Okonkwo",
                defaults={
                    "relationship": FamilyMember.Relationship.CHILD,
                    "phone": "+2348098765432",
                    "has_gate_access": True,
                },
            )
            self.summary.bump("family_members", created=created)
            _, created = Vehicle.objects.get_or_create(
                estate=ctx.estate,
                owner=r1,
                license_plate="LAG-DEMO-101",
                defaults={
                    "vehicle_type": Vehicle.VehicleType.CAR,
                    "make": "Toyota",
                    "model": "Camry",
                    "color": "Black",
                },
            )
            self.summary.bump("vehicles", created=created)
        else:
            self._resident(
                ctx,
                key="owner",
                user_key="resident1",
                unit_key="T1-501",
                resident_type=ResidentProfile.ResidentType.OWNER,
                status=ResidentProfile.Status.ACTIVE,
            )

    def _seed_billing(self, ctx: EstateContext) -> None:
        resident = ctx.residents["owner"]
        unit = ctx.units["A-101"]
        fee_type, created = FeeType.objects.get_or_create(
            estate=ctx.estate,
            code="service_charge",
            defaults={
                "name": "Monthly Service Charge",
                "amount": Decimal("75000.00"),
                "frequency": FeeType.Frequency.MONTHLY,
            },
        )
        self.summary.bump("fee_types", created=created)

        invoice, created = Invoice.objects.get_or_create(
            estate=ctx.estate,
            invoice_number="INV-DEMO-2026-0001",
            defaults={
                "unit": unit,
                "resident": resident,
                "status": Invoice.Status.ISSUED,
                "due_date": timezone.now().date() + timedelta(days=14),
                "subtotal": Decimal("75000.00"),
                "total_amount": Decimal("75000.00"),
                "currency": "NGN",
            },
        )
        self.summary.bump("invoices", created=created)
        if created:
            InvoiceLine.objects.create(
                estate=ctx.estate,
                invoice=invoice,
                fee_type=fee_type,
                description="Service charge — current month",
                quantity=Decimal("1"),
                unit_price=Decimal("75000.00"),
                amount=Decimal("75000.00"),
            )

        overdue_inv, created = Invoice.objects.get_or_create(
            estate=ctx.estate,
            invoice_number="INV-DEMO-2026-0002",
            defaults={
                "unit": ctx.units["A-103"],
                "resident": ctx.residents["tenant"],
                "status": Invoice.Status.OVERDUE,
                "due_date": timezone.now().date() - timedelta(days=21),
                "subtotal": Decimal("75000.00"),
                "total_amount": Decimal("75000.00"),
                "currency": "NGN",
            },
        )
        self.summary.bump("invoices", created=created)

        _, created = Payment.objects.get_or_create(
            estate=ctx.estate,
            reference="PAY-DEMO-2026-0001",
            defaults={
                "invoice": invoice,
                "payer": ctx.users["resident1"],
                "amount": Decimal("25000.00"),
                "currency": "NGN",
                "status": Payment.Status.COMPLETED,
                "method": Payment.Method.BANK_TRANSFER,
                "paid_at": timezone.now() - timedelta(days=2),
            },
        )
        self.summary.bump("payments", created=created)

        _, created = DebtRecord.objects.get_or_create(
            estate=ctx.estate,
            unit=ctx.units["A-103"],
            defaults={
                "resident": ctx.residents["tenant"],
                "total_debt": Decimal("75000.00"),
                "overdue_amount": Decimal("75000.00"),
                "status": DebtRecord.Status.OVERDUE,
                "oldest_due_date": overdue_inv.due_date,
            },
        )
        self.summary.bump("debt_records", created=created)

        _, created = PaymentProviderConfig.objects.get_or_create(
            estate=ctx.estate,
            provider=PaymentProviderConfig.Provider.PAYSTACK,
            defaults={
                "is_default": True,
                "is_active": True,
                "public_key": "pk_test_demo_estateos",
                "secret_key_encrypted": "sk_test_demo_estateos",
                "supported_currencies": ["NGN"],
                "supported_methods": ["card", "bank_transfer"],
            },
        )
        self.summary.bump("payment_providers", created=created)

    def _seed_visitors(self, ctx: EstateContext) -> None:
        host = ctx.residents["owner"]
        admin = ctx.users["admin"]
        pass_obj, created = VisitorPass.objects.get_or_create(
            estate=ctx.estate,
            qr_code="QR-DEMO-PALM-001",
            defaults={
                "host": host,
                "visitor_name": "Delivery Agent",
                "visitor_phone": "+2348066666001",
                "pass_type": VisitorPass.PassType.SINGLE,
                "valid_until": timezone.now() + timedelta(hours=4),
                "purpose": "Package delivery",
            },
        )
        self.summary.bump("visitor_passes", created=created)

        _, created = VisitorLog.objects.get_or_create(
            estate=ctx.estate,
            visitor_pass=pass_obj,
            direction=VisitorLog.Direction.ENTRY,
            defaults={
                "visitor_name": pass_obj.visitor_name,
                "host": host,
                "verification_method": VisitorLog.VerificationMethod.QR,
                "gate_name": "Main Gate",
                "verified_by": admin,
            },
        )
        self.summary.bump("visitor_logs", created=created)

        _, created = Blacklist.objects.get_or_create(
            estate=ctx.estate,
            phone="+2348077777001",
            defaults={
                "full_name": "Blocked Visitor Demo",
                "reason": Blacklist.Reason.TRESPASS,
                "description": "Previously trespassed — QA blacklist check",
                "reported_by": admin,
            },
        )
        self.summary.bump("blacklist", created=created)

    def _seed_security(self, ctx: EstateContext) -> None:
        admin = ctx.users["admin"]
        staff = ctx.users["security_staff"]
        _, created = Incident.objects.get_or_create(
            estate=ctx.estate,
            title="Noise complaint — Block B",
            defaults={
                "description": "Loud music reported after quiet hours.",
                "category": Incident.Category.NOISE,
                "severity": Incident.Severity.MEDIUM,
                "status": Incident.Status.INVESTIGATING,
                "location": "Block B courtyard",
                "reported_by": ctx.users["resident1"],
                "assigned_to": staff,
            },
        )
        self.summary.bump("incidents", created=created)

        _, created = PatrolLog.objects.get_or_create(
            estate=ctx.estate,
            officer=staff,
            checkpoint="North Perimeter",
            defaults={
                "route_name": "Evening Route A",
                "status": PatrolLog.Status.COMPLETED,
            },
        )
        self.summary.bump("patrol_logs", created=created)

        _, created = SOSAlert.objects.get_or_create(
            estate=ctx.estate,
            resident=ctx.residents["owner"],
            status=SOSAlert.Status.ACKNOWLEDGED,
            defaults={
                "message": "Demo SOS — resolved after wellness check",
                "location_description": "Unit A-101",
                "acknowledged_by": admin,
                "acknowledged_at": timezone.now() - timedelta(hours=1),
            },
        )
        self.summary.bump("sos_alerts", created=created)

        _, created = EmergencyBroadcast.objects.get_or_create(
            estate=ctx.estate,
            title="Scheduled power maintenance",
            defaults={
                "message": "Brief outage expected Saturday 2–4am for transformer upgrade.",
                "priority": EmergencyBroadcast.Priority.WARNING,
                "channel": EmergencyBroadcast.Channel.ALL,
                "sent_by": admin,
            },
        )
        self.summary.bump("emergency_broadcasts", created=created)

    def _seed_maintenance(self, ctx: EstateContext) -> None:
        sla, created = SLAConfig.objects.get_or_create(
            estate=ctx.estate,
            priority=SLAConfig.Priority.HIGH,
            category="plumbing",
            defaults={
                "name": "High priority plumbing",
                "response_time_hours": 4,
                "resolution_time_hours": 24,
            },
        )
        self.summary.bump("sla_configs", created=created)

        _, created = Ticket.objects.get_or_create(
            estate=ctx.estate,
            ticket_number="MT-DEMO-0001",
            defaults={
                "title": "Kitchen sink leak",
                "description": "Water pooling under kitchen sink in A-101.",
                "category": Ticket.Category.PLUMBING,
                "priority": Ticket.Priority.HIGH,
                "status": Ticket.Status.IN_PROGRESS,
                "unit": ctx.units["A-101"],
                "reported_by": ctx.users["resident1"],
                "assigned_to": ctx.users["technician"],
                "sla_config": sla,
                "due_at": timezone.now() + timedelta(hours=12),
            },
        )
        self.summary.bump("tickets", created=created)

        _, created = Ticket.objects.get_or_create(
            estate=ctx.estate,
            ticket_number="MT-DEMO-0002",
            defaults={
                "title": "Elevator inspection follow-up",
                "description": "Routine elevator maintenance ticket for QA.",
                "category": Ticket.Category.GENERAL,
                "priority": Ticket.Priority.MEDIUM,
                "status": Ticket.Status.OPEN,
                "unit": ctx.units["B-201"],
                "reported_by": ctx.users["admin"],
            },
        )
        self.summary.bump("tickets", created=created)

    def _seed_facilities(self, ctx: EstateContext) -> None:
        gym, created = Facility.objects.get_or_create(
            estate=ctx.estate,
            slug="community-gym",
            defaults={
                "name": "Community Gym",
                "facility_type": Facility.FacilityType.GYM,
                "description": "Fully equipped resident gym",
                "capacity": 20,
                "hourly_rate": Decimal("0.00"),
            },
        )
        self.summary.bump("facilities", created=created)

        _, created = Booking.objects.get_or_create(
            estate=ctx.estate,
            facility=gym,
            user=ctx.users["resident1"],
            notes="[DEMO-BOOK-001] Demo seed gym booking",
            defaults={
                "resident": ctx.residents["owner"],
                "status": Booking.Status.CONFIRMED,
                "start_time": timezone.now() + timedelta(days=1, hours=2),
                "end_time": timezone.now() + timedelta(days=1, hours=4),
                "guest_count": 1,
            },
        )
        self.summary.bump("bookings", created=created)

    def _seed_packages(self, ctx: EstateContext) -> None:
        pkg, created = Package.objects.get_or_create(
            estate=ctx.estate,
            tracking_number="PKG-DEMO-001",
            defaults={
                "recipient": ctx.residents["owner"],
                "unit": ctx.units["A-101"],
                "status": Package.Status.NOTIFIED,
                "carrier": "DHL",
                "sender_name": "Amazon",
                "description": "Medium brown box",
                "received_at": timezone.now() - timedelta(hours=3),
                "storage_location": "Gate House Locker 3",
                "otp_code": "482910",
            },
        )
        self.summary.bump("packages", created=created)
        if created:
            PackageLog.objects.create(
                estate=ctx.estate,
                package=pkg,
                previous_status=Package.Status.RECEIVED,
                new_status=Package.Status.NOTIFIED,
                changed_by=ctx.users["security_staff"],
                notes="Resident notified via SMS",
            )

    def _seed_parking(self, ctx: EstateContext) -> None:
        slot, created = ParkingSlot.objects.get_or_create(
            estate=ctx.estate,
            slot_number="P-A101",
            defaults={
                "slot_type": ParkingSlot.SlotType.RESIDENT,
                "status": ParkingSlot.Status.OCCUPIED,
                "block": ctx.blocks["A"],
                "unit": ctx.units["A-101"],
                "location": "Block A basement",
            },
        )
        self.summary.bump("parking_slots", created=created)

        vehicle = Vehicle.objects.get(estate=ctx.estate, owner=ctx.residents["owner"])
        _, created = ParkingPermit.objects.get_or_create(
            estate=ctx.estate,
            permit_number="PRK-DEMO-001",
            defaults={
                "slot": slot,
                "resident": ctx.residents["owner"],
                "vehicle": vehicle,
                "status": ParkingPermit.Status.ACTIVE,
                "valid_from": timezone.now().date(),
                "valid_until": timezone.now().date() + timedelta(days=365),
            },
        )
        self.summary.bump("parking_permits", created=created)

    def _seed_utilities(self, ctx: EstateContext) -> None:
        account, created = UtilityAccount.objects.get_or_create(
            estate=ctx.estate,
            utility_type=UtilityAccount.UtilityType.ELECTRICITY,
            account_number="ELEC-DEMO-A101",
            defaults={
                "unit": ctx.units["A-101"],
                "meter_number": "MTR-10001",
                "provider_name": "EKEDC",
                "current_balance": Decimal("3500.00"),
                "last_reading": Decimal("4521.5000"),
                "last_reading_date": timezone.now().date() - timedelta(days=7),
            },
        )
        self.summary.bump("utility_accounts", created=created)

        _, created = UtilityTransaction.objects.get_or_create(
            estate=ctx.estate,
            reference="UTIL-DEMO-001",
            defaults={
                "account": account,
                "user": ctx.users["resident1"],
                "transaction_type": UtilityTransaction.TransactionType.PURCHASE,
                "amount": Decimal("10000.00"),
                "token": "1234-5678-9012",
                "status": UtilityTransaction.Status.COMPLETED,
                "completed_at": timezone.now() - timedelta(days=1),
            },
        )
        self.summary.bump("utility_transactions", created=created)

    def _seed_marketplace(self, ctx: EstateContext) -> None:
        vendor_user = ctx.users["vendor"]
        vendor, created = Vendor.objects.get_or_create(
            estate=ctx.estate,
            slug="fresh-mart-demo",
            defaults={
                "user": vendor_user,
                "business_name": "Fresh Mart Demo",
                "category": "groceries",
                "status": Vendor.Status.ACTIVE,
                "phone": "+2348011111001",
                "email": vendor_user.email,
            },
        )
        self.summary.bump("vendors", created=created)

        product, created = Product.objects.get_or_create(
            estate=ctx.estate,
            slug="organic-eggs-demo",
            defaults={
                "vendor": vendor,
                "name": "Organic Eggs (12 pack)",
                "category": "dairy",
                "price": Decimal("3500.00"),
                "stock_quantity": 50,
                "status": Product.Status.ACTIVE,
            },
        )
        self.summary.bump("products", created=created)

        _, created = Order.objects.get_or_create(
            estate=ctx.estate,
            order_number="ORD-DEMO-0001",
            defaults={
                "user": ctx.users["resident1"],
                "vendor": vendor,
                "unit": ctx.units["A-101"],
                "status": Order.Status.PENDING,
                "items": [
                    {
                        "product_id": str(product.id),
                        "name": product.name,
                        "quantity": 2,
                        "unit_price": str(product.price),
                    }
                ],
                "subtotal": Decimal("7000.00"),
                "delivery_fee": Decimal("500.00"),
                "total_amount": Decimal("7500.00"),
                "currency": "NGN",
                "delivery_address": "Unit A-101, Palm Grove Demo",
            },
        )
        self.summary.bump("marketplace_orders", created=created)

    def _seed_community(self, ctx: EstateContext) -> None:
        author = ctx.users["resident1"]
        post, created = Post.objects.get_or_create(
            estate=ctx.estate,
            title="Welcome new neighbours!",
            defaults={
                "author": author,
                "body": "Looking forward to the estate BBQ this weekend.",
                "status": Post.Status.PUBLISHED,
                "category": "general",
                "is_pinned": True,
            },
        )
        self.summary.bump("posts", created=created)

        _, created = Comment.objects.get_or_create(
            estate=ctx.estate,
            post=post,
            author=ctx.users["admin"],
            defaults={"body": "See you at the clubhouse on Saturday."},
        )
        self.summary.bump("comments", created=created)

        _, created = Poll.objects.get_or_create(
            estate=ctx.estate,
            question="Preferred pool maintenance day?",
            defaults={
                "created_by": ctx.users["admin"],
                "options": ["Monday", "Wednesday", "Friday"],
                "status": Poll.Status.ACTIVE,
                "closes_at": timezone.now() + timedelta(days=7),
            },
        )
        self.summary.bump("polls", created=created)

        _, created = Announcement.objects.get_or_create(
            estate=ctx.estate,
            title="Estate security drill",
            defaults={
                "body": "A routine security drill is scheduled for next Tuesday at 10:00.",
                "priority": Announcement.Priority.IMPORTANT,
                "published_by": ctx.users["security_admin"],
            },
        )
        self.summary.bump("announcements", created=created)

        _, created = LostFound.objects.get_or_create(
            estate=ctx.estate,
            title="Found set of keys",
            defaults={
                "reported_by": ctx.users["security_staff"],
                "item_type": LostFound.ItemType.FOUND,
                "status": LostFound.Status.OPEN,
                "description": "Brass keys found near Block A lobby — QA lost & found item.",
                "location": "Block A lobby",
                "found_date": timezone.now().date(),
            },
        )
        self.summary.bump("lost_found", created=created)

    def _seed_healthcare(self, ctx: EstateContext) -> None:
        hospital, created = Hospital.objects.get_or_create(
            estate=ctx.estate,
            slug="demo-clinic",
            defaults={
                "name": "Palm Grove Partner Clinic",
                "address": "14 Wellness Road, Lagos",
                "phone": "+2348090001001",
                "email": "clinic@demo.estateos",
                "specialties": ["general", "pediatrics"],
            },
        )
        self.summary.bump("hospitals", created=created)

        _, created = Appointment.objects.get_or_create(
            estate=ctx.estate,
            resident=ctx.residents["owner"],
            hospital=hospital,
            reason="[DEMO-APT-001] Annual check-up",
            defaults={
                "doctor_name": "Dr. Adebayo",
                "specialty": "general",
                "status": Appointment.Status.CONFIRMED,
                "scheduled_at": timezone.now() + timedelta(days=5, hours=10),
            },
        )
        self.summary.bump("appointments", created=created)

    def _seed_pharmacy(self, ctx: EstateContext) -> None:
        rx, created = Prescription.objects.get_or_create(
            estate=ctx.estate,
            prescription_number="RX-DEMO-001",
            defaults={
                "resident": ctx.residents["owner"],
                "doctor_name": "Dr. Adebayo",
                "hospital_name": "Palm Grove Partner Clinic",
                "status": Prescription.Status.VERIFIED,
                "medications": [{"name": "Amoxicillin", "dosage": "500mg"}],
                "issued_date": date.today() - timedelta(days=3),
                "expiry_date": date.today() + timedelta(days=27),
                "verified_by": ctx.users["admin"],
                "verified_at": timezone.now() - timedelta(days=2),
                "image": ContentFile(MINIMAL_PNG, name="rx-demo.png"),
            },
        )
        self.summary.bump("prescriptions", created=created)

        _, created = MedicationOrder.objects.get_or_create(
            estate=ctx.estate,
            order_number="MED-DEMO-001",
            defaults={
                "prescription": rx,
                "resident": ctx.residents["owner"],
                "status": MedicationOrder.Status.CONFIRMED,
                "items": rx.medications,
                "total_amount": Decimal("4500.00"),
                "currency": "NGN",
                "delivery_address": "Unit A-101",
            },
        )
        self.summary.bump("medication_orders", created=created)

    def _seed_transportation(self, ctx: EstateContext) -> None:
        _, created = RideRequest.objects.get_or_create(
            estate=ctx.estate,
            pickup_address="Palm Grove Demo — Main Gate",
            dropoff_address="Victoria Island, Lagos",
            defaults={
                "requester": ctx.users["resident1"],
                "status": RideRequest.Status.REQUESTED,
                "ride_type": RideRequest.RideType.STANDARD,
                "estimated_fare": Decimal("4500.00"),
                "passenger_count": 1,
            },
        )
        self.summary.bump("ride_requests", created=created)

    def _seed_analytics(self, ctx: EstateContext) -> None:
        now = timezone.now()
        metrics = [
            ("residents.active", "Active Residents", Decimal("3"), "count"),
            ("visitors.today", "Visitors Today", Decimal("12"), "count"),
            ("maintenance.open", "Open Tickets", Decimal("2"), "count"),
            ("billing.pending_ngn", "Pending Invoices (NGN)", Decimal("150000"), "NGN"),
        ]
        for key, name, value, unit in metrics:
            _, created = MetricSnapshot.objects.get_or_create(
                estate=ctx.estate,
                metric_key=key,
                recorded_at=now.replace(minute=0, second=0, microsecond=0),
                defaults={
                    "metric_name": name,
                    "value": value,
                    "unit": unit,
                    "period_start": now - timedelta(days=30),
                    "period_end": now,
                    "metadata": {"demo_seed": DEMO_MARKER},
                },
            )
            self.summary.bump("metric_snapshots", created=created)

        _, created = DashboardWidget.objects.get_or_create(
            estate=ctx.estate,
            slug="visitor-trends",
            defaults={
                "name": "Visitor Trends",
                "widget_type": DashboardWidget.WidgetType.CHART,
                "description": "Monthly visitor volume",
                "query_config": {"metric_key": "visitors.today"},
                "display_config": {"chart": "area"},
                "allowed_roles": ["estate_admin", "security_admin"],
            },
        )
        self.summary.bump("dashboard_widgets", created=created)

    def _seed_notifications(self, ctx: EstateContext) -> None:
        template, created = NotificationTemplate.objects.get_or_create(
            estate=ctx.estate,
            code="package_ready",
            channel=NotificationTemplate.Channel.INAPP,
            locale="en",
            defaults={
                "name": "Package Ready",
                "subject": "Package ready for pickup",
                "body_template": "Your package {{tracking_number}} is ready at {{location}}.",
                "variables": ["tracking_number", "location"],
            },
        )
        self.summary.bump("notification_templates", created=created)

        _, created = Notification.objects.get_or_create(
            estate=ctx.estate,
            recipient=ctx.users["resident1"],
            title="Package ready for pickup",
            defaults={
                "template": template,
                "channel": NotificationTemplate.Channel.INAPP,
                "status": Notification.Status.DELIVERED,
                "body": "Your package PKG-DEMO-001 is ready at Gate House Locker 3.",
                "data": {"tracking_number": "PKG-DEMO-001"},
                "delivered_at": timezone.now() - timedelta(hours=1),
            },
        )
        self.summary.bump("notifications", created=created)

    def _seed_ai(self, ctx: EstateContext) -> None:
        conv, created = Conversation.objects.get_or_create(
            estate=ctx.estate,
            user=ctx.users["resident1"],
            title="Billing question",
            defaults={
                "status": Conversation.Status.ACTIVE,
                "context": {"topic": "billing"},
                "message_count": 2,
                "last_message_at": timezone.now() - timedelta(hours=5),
            },
        )
        self.summary.bump("ai_conversations", created=created)

        doc, created = Document.objects.get_or_create(
            estate=ctx.estate,
            title="Estate handbook",
            defaults={
                "document_type": Document.DocumentType.POLICY,
                "status": Document.Status.INDEXED,
                "content_text": "Quiet hours are 10pm to 6am. Visitor passes required after 8pm.",
                "uploaded_by": ctx.users["admin"],
                "chunk_count": 1,
            },
        )
        self.summary.bump("ai_documents", created=created)

        _, created = Prediction.objects.get_or_create(
            estate=ctx.estate,
            prediction_type=Prediction.PredictionType.PAYMENT,
            target_entity_type="resident_profile",
            target_entity_id=ctx.residents["tenant"].id,
            defaults={
                "score": Decimal("0.7200"),
                "confidence": Decimal("0.8100"),
                "prediction_data": {"risk": "medium", "days_overdue": 21},
                "model_name": "payment-default-v1",
                "valid_until": timezone.now() + timedelta(days=30),
            },
        )
        self.summary.bump("ai_predictions", created=created)
        if created and doc:
            pass  # document indexed standalone

    def _sync_estate_counts(self, ctx: EstateContext) -> None:
        occupied = Unit.objects.filter(
            estate=ctx.estate,
            occupancy_status=Unit.OccupancyStatus.OCCUPIED,
            is_active=True,
        ).count()
        total = Unit.objects.filter(estate=ctx.estate, is_active=True).count()
        ctx.estate.occupied_units = occupied
        ctx.estate.total_units = max(ctx.estate.total_units, total)
        ctx.estate.save(update_fields=["occupied_units", "total_units", "updated_at"])


def run_demo_seed(*, flush: bool = False, verbosity: int = 1) -> SeedSummary:
    return DemoSeeder(flush=flush, verbosity=verbosity).run()
