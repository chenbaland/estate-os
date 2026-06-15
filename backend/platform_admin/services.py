"""Platform-level estate provisioning and admin assignment."""
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from accounts.models import Role, User, UserRole
from estates.models import Estate


@dataclass(frozen=True)
class AssignAdminResult:
    user: User
    user_role: UserRole
    created_user: bool
    temporary_password: str | None

DEFAULT_ESTATE_ROLES = [
    (Role.RoleCode.ESTATE_ADMIN, "Estate Admin", 10),
    (Role.RoleCode.FACILITY_ADMIN, "Facility Admin", 8),
    (Role.RoleCode.SECURITY_ADMIN, "Security Admin", 8),
    (Role.RoleCode.FINANCE_ADMIN, "Finance Admin", 8),
    (Role.RoleCode.RESIDENT, "Resident", 0),
    (Role.RoleCode.VENDOR, "Vendor", 0),
    (Role.RoleCode.TECHNICIAN, "Technician", 0),
    (Role.RoleCode.SECURITY_PERSONNEL, "Security Personnel", 0),
]

ADMIN_ROLE_CODES = {
    Role.RoleCode.ESTATE_ADMIN,
    Role.RoleCode.FACILITY_ADMIN,
    Role.RoleCode.SECURITY_ADMIN,
    Role.RoleCode.FINANCE_ADMIN,
}


def unique_estate_slug(name: str) -> str:
    base = slugify(name)[:90] or "estate"
    slug = base
    counter = 1
    while Estate.all_objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


@transaction.atomic
def seed_estate_roles(estate: Estate) -> None:
    for code, name, priority in DEFAULT_ESTATE_ROLES:
        Role.objects.get_or_create(
            estate=estate,
            code=code,
            defaults={
                "name": name,
                "is_system_role": True,
                "priority": priority,
            },
        )


@transaction.atomic
def create_estate(validated_data: dict) -> Estate:
    if not validated_data.get("slug"):
        validated_data["slug"] = unique_estate_slug(validated_data["name"])
    estate = Estate.objects.create(onboarded_at=timezone.now(), **validated_data)
    seed_estate_roles(estate)
    return estate


@transaction.atomic
def assign_estate_admin(
    *,
    email: str,
    estate: Estate,
    role_code: str,
    assigned_by: User,
    first_name: str = "",
    last_name: str = "",
) -> AssignAdminResult:
    if role_code not in ADMIN_ROLE_CODES:
        raise ValueError("Invalid admin role for estate assignment.")

    created_user = False
    temporary_password = None
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        temporary_password = get_random_string(16)
        username_base = email.split("@")[0][:140]
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            password=temporary_password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
        )
        created_user = True

    role = Role.objects.filter(estate=estate, code=role_code, is_active=True).first()
    if role is None:
        seed_estate_roles(estate)
        role = Role.objects.get(estate=estate, code=role_code, is_active=True)
    user_role, _ = UserRole.objects.update_or_create(
        user=user,
        role=role,
        estate=estate,
        defaults={
            "assigned_by": assigned_by,
            "is_active": True,
        },
    )
    return AssignAdminResult(
        user=user,
        user_role=user_role,
        created_user=created_user,
        temporary_password=temporary_password,
    )
