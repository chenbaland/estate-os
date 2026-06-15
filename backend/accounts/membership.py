"""User estate membership helpers for registration and activation flows."""
from django.db import transaction

from accounts.models import Role, User, UserRole
from estates.models import Estate, Unit
from notifications.models import Notification, NotificationTemplate
from residents.models import ResidentProfile


RESIDENT_TYPE_LABELS = {
    ResidentProfile.ResidentType.OWNER: "Homeowner",
    ResidentProfile.ResidentType.TENANT: "Tenant",
}


def get_user_memberships(user: User) -> list[dict]:
    """Return resident profiles and active roles for the authenticated user."""
    profiles = (
        ResidentProfile.objects.filter(user=user)
        .select_related("estate", "unit")
        .order_by("-created_at")
    )
    memberships = [
        {
            "resident_profile_id": str(profile.id),
            "estate_id": str(profile.estate_id),
            "estate_name": profile.estate.name,
            "estate_slug": profile.estate.slug,
            "resident_type": profile.resident_type or None,
            "resident_type_label": RESIDENT_TYPE_LABELS.get(
                profile.resident_type,
                "Not assigned",
            )
            if profile.resident_type
            else "Not assigned",
            "status": profile.status,
            "unit_id": str(profile.unit_id) if profile.unit_id else None,
            "unit_number": profile.unit.unit_number if profile.unit_id else None,
        }
        for profile in profiles
    ]

    active_roles = (
        UserRole.objects.filter(user=user, is_active=True)
        .select_related("role", "estate")
        .order_by("-role__priority", "estate__name")
    )
    roles = [
        {
            "id": str(user_role.id),
            "code": user_role.role.code,
            "name": user_role.role.name,
            "estate_id": str(user_role.estate_id),
            "estate_name": user_role.estate.name,
        }
        for user_role in active_roles
    ]

    if user.is_superuser and not any(role["code"] == Role.RoleCode.SUPER_ADMIN for role in roles):
        roles.insert(
            0,
            {
                "id": "platform-super-admin",
                "code": Role.RoleCode.SUPER_ADMIN,
                "name": "Super Admin",
                "estate_id": "",
                "estate_name": "Platform",
            },
        )

    has_active_membership = any(
        profile.status == ResidentProfile.Status.ACTIVE for profile in profiles
    ) or bool(roles) or user.is_superuser

    pending_membership = (
        any(profile.status == ResidentProfile.Status.PENDING for profile in profiles)
        and not user.is_superuser
    )

    return {
        "memberships": memberships,
        "roles": roles,
        "has_active_membership": has_active_membership,
        "pending_membership": pending_membership,
    }


def get_or_create_resident_role(estate: Estate) -> Role:
    role, _ = Role.objects.get_or_create(
        estate=estate,
        code=Role.RoleCode.RESIDENT,
        defaults={
            "name": "Resident",
            "description": "Estate resident with standard access",
            "is_system_role": True,
            "priority": 0,
        },
    )
    return role


def _notify_estate_admins(profile: ResidentProfile) -> None:
    admin_roles = UserRole.objects.filter(
        estate=profile.estate,
        is_active=True,
        role__code__in=[Role.RoleCode.ESTATE_ADMIN, Role.RoleCode.FINANCE_ADMIN],
    ).select_related("user")

    user = profile.user
    unit_label = profile.unit.unit_number if profile.unit_id else "unassigned"
    title = "New resident registration"
    body = (
        f"{user.get_full_name() or user.email} registered for unit {unit_label} "
        f"and is awaiting approval."
    )

    for admin_role in admin_roles:
        Notification.objects.create(
            estate=profile.estate,
            recipient=admin_role.user,
            channel=NotificationTemplate.Channel.INAPP,
            status=Notification.Status.DELIVERED,
            priority=Notification.Priority.HIGH,
            title=title,
            body=body,
            data={
                "type": "resident_registration",
                "resident_profile_id": str(profile.id),
                "user_id": str(user.id),
            },
            action_url=f"/residents?pending={profile.id}",
        )

def _notify_resident(profile: ResidentProfile, *, title: str, body: str) -> None:
    Notification.objects.create(
        estate=profile.estate,
        recipient=profile.user,
        channel=NotificationTemplate.Channel.INAPP,
        status=Notification.Status.DELIVERED,
        priority=Notification.Priority.NORMAL,
        title=title,
        body=body,
        data={
            "type": "resident_activation",
            "resident_profile_id": str(profile.id),
        },
    )


@transaction.atomic
def register_resident_for_estate(
    user: User,
    estate: Estate,
    *,
    unit: Unit,
) -> ResidentProfile:
    existing = ResidentProfile.objects.filter(user=user, estate=estate).exclude(
        status=ResidentProfile.Status.INACTIVE,
    )
    if existing.filter(status=ResidentProfile.Status.ACTIVE).exists():
        raise ValueError("You are already an active resident of this estate.")
    if existing.filter(status=ResidentProfile.Status.PENDING).exists():
        raise ValueError("You already have a pending registration for this estate.")

    if unit.estate_id != estate.id:
        raise ValueError("Unit must belong to the selected estate.")
    if unit.occupancy_status != Unit.OccupancyStatus.VACANT:
        raise ValueError("This unit is not available.")
    if ResidentProfile.objects.filter(
        unit=unit,
        status__in=[ResidentProfile.Status.PENDING, ResidentProfile.Status.ACTIVE],
    ).exists():
        raise ValueError("This unit already has a resident assigned.")

    profile = ResidentProfile.objects.create(
        estate=estate,
        user=user,
        unit=unit,
        status=ResidentProfile.Status.PENDING,
        is_primary=True,
    )
    _notify_estate_admins(profile)
    return profile


@transaction.atomic
def activate_resident_profile(
    profile: ResidentProfile,
    *,
    activated_by: User,
    resident_type: str,
    unit: Unit | None = None,
) -> ResidentProfile:
    if profile.status != ResidentProfile.Status.PENDING:
        raise ValueError("Only pending resident profiles can be activated.")

    if resident_type not in (
        ResidentProfile.ResidentType.OWNER,
        ResidentProfile.ResidentType.TENANT,
    ):
        raise ValueError("resident_type must be owner or tenant.")

    if unit is None and profile.unit_id:
        unit = profile.unit
    if unit is None:
        raise ValueError("A unit must be assigned before activation.")
    if unit.estate_id != profile.estate_id:
        raise ValueError("Unit must belong to the same estate.")

    profile.unit = unit
    profile.resident_type = resident_type
    profile.status = ResidentProfile.Status.ACTIVE
    profile.is_primary = True
    if not profile.move_in_date:
        from django.utils import timezone

        profile.move_in_date = timezone.now().date()
    profile.save(
        update_fields=[
            "unit",
            "resident_type",
            "status",
            "is_primary",
            "move_in_date",
            "updated_at",
        ],
    )

    resident_role = get_or_create_resident_role(profile.estate)
    UserRole.objects.update_or_create(
        user=profile.user,
        role=resident_role,
        estate=profile.estate,
        defaults={
            "assigned_by": activated_by,
            "is_active": True,
        },
    )

    if profile.resident_type == ResidentProfile.ResidentType.OWNER:
        unit.owner = profile.user
        unit.occupancy_status = Unit.OccupancyStatus.OCCUPIED
        unit.save(update_fields=["owner", "occupancy_status", "updated_at"])
    elif profile.resident_type == ResidentProfile.ResidentType.TENANT:
        unit.occupancy_status = Unit.OccupancyStatus.OCCUPIED
        unit.save(update_fields=["occupancy_status", "updated_at"])

    type_label = RESIDENT_TYPE_LABELS.get(resident_type, resident_type)
    unit_label = unit.unit_number
    _notify_resident(
        profile,
        title="Resident profile approved",
        body=(
            f"Your resident profile for {profile.estate.name} has been approved "
            f"as a {type_label.lower()}. Unit: {unit_label}."
        ),
    )
    return profile
