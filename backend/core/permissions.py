"""
Role-based access control permission classes for EstateOS.
"""
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Platform-level super administrator."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsEstateAdmin(BasePermission):
    """Estate administrator with full estate-scoped access."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.roles.filter(
            code="estate_admin",
            estate_id=getattr(request, "estate_id", None),
            is_active=True,
        ).exists()


class HasRole(BasePermission):
    """Permission check against one or more role codes."""

    required_roles: list[str] = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        roles = getattr(view, "required_roles", None) or self.required_roles
        if not roles:
            return True

        estate_id = getattr(request, "estate_id", None)
        qs = request.user.roles.filter(code__in=roles, is_active=True)
        if estate_id:
            qs = qs.filter(estate_id=estate_id)
        return qs.exists()


class HasPermission(BasePermission):
    """Permission check against granular permission codes."""

    required_permissions: list[str] = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        permissions = getattr(view, "required_permissions", None) or self.required_permissions
        if not permissions:
            return True

        estate_id = getattr(request, "estate_id", None)
        user_permissions = request.user.get_permission_codes(estate_id=estate_id)
        return all(p in user_permissions for p in permissions)


class IsTenantMember(BasePermission):
    """User must belong to the resolved estate tenant."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        estate_id = getattr(request, "estate_id", None)
        if not estate_id:
            return False
        from accounts.models import UserRole

        return UserRole.objects.filter(
            user=request.user,
            estate_id=estate_id,
            is_active=True,
        ).exists()


class IsOwnerOrEstateAdmin(BasePermission):
    """Object owner or estate admin."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if IsEstateAdmin().has_permission(request, view):
            return True
        owner = getattr(obj, self.owner_field, None)
        if owner is None:
            owner = getattr(obj, "created_by", None)
        return owner == request.user


class ReadOnly(BasePermission):
    """Allow read-only access."""

    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")
