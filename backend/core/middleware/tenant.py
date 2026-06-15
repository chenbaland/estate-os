"""
Multi-tenant middleware for estate-scoped request context.

Resolves the active estate from headers or subdomain and attaches it to
the request for downstream ORM filtering and permission checks.
"""
import logging
from typing import Optional

from django.conf import settings
from django.http import Http404

logger = logging.getLogger("estateos.tenant")


class TenantMiddleware:
    """Resolve and attach tenant (estate) context to each request."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.tenant_header = getattr(settings, "TENANT_HEADER", "X-Estate-Id")
        self.tenant_slug_header = getattr(settings, "TENANT_SLUG_HEADER", "X-Tenant-Slug")
        self.exempt_prefixes = getattr(settings, "TENANT_EXEMPT_URL_PREFIXES", ())

    def __call__(self, request):
        request.estate = None
        request.estate_id = None

        if not self._is_exempt(request.path):
            estate = self._resolve_estate(request)
            if estate:
                request.estate = estate
                request.estate_id = estate.id

        response = self.get_response(request)
        if request.estate_id:
            response["X-Estate-Id"] = str(request.estate_id)
        return response

    def _is_exempt(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.exempt_prefixes)

    def _resolve_estate(self, request):
        from estates.models import Estate

        estate_id = request.META.get(f"HTTP_{self.tenant_header.upper().replace('-', '_')}")
        slug = request.META.get(f"HTTP_{self.tenant_slug_header.upper().replace('-', '_')}")

        if not estate_id and not slug:
            subdomain = self._extract_subdomain(request)
            if subdomain and subdomain not in ("www", "api", "admin"):
                slug = subdomain

        estate = None
        if estate_id:
            try:
                estate = Estate.objects.get(id=estate_id, is_deleted=False, is_active=True)
            except (Estate.DoesNotExist, ValueError):
                logger.warning("Invalid estate_id header: %s", estate_id)
                raise Http404("Estate not found")
        elif slug:
            try:
                estate = Estate.objects.get(slug=slug, is_deleted=False, is_active=True)
            except Estate.DoesNotExist:
                logger.warning("Invalid estate slug: %s", slug)
                raise Http404("Estate not found")

        return estate

    def _extract_subdomain(self, request) -> Optional[str]:
        host = request.get_host().split(":")[0]
        parts = host.split(".")
        if len(parts) >= 3:
            return parts[0]
        return None
