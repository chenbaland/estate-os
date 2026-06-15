"""Estate, block, and unit CRUD and tenancy tests."""
from decimal import Decimal

import pytest
from django.http import Http404
from rest_framework.test import APIRequestFactory, force_authenticate

from core.middleware.tenant import TenantMiddleware
from estates.models import Block, Estate, Unit
from estates.serializers import EstateSerializer, UnitSerializer
from estates.views import EstateViewSet


@pytest.mark.django_db
class TestEstateCRUD:
    def test_create_estate(self, db):
        estate = Estate.objects.create(
            name="Sunset Villas",
            slug="sunset-villas",
            address_line1="1 Sunset Road",
            city="Port Harcourt",
            state="Rivers",
        )
        assert estate.is_active is True
        assert str(estate) == "Sunset Villas"

    def test_estate_soft_delete(self, estate):
        estate.soft_delete()
        estate.refresh_from_db()
        assert estate.is_deleted is True
        assert Estate.objects.filter(id=estate.id).count() == 0
        assert Estate.all_objects.filter(id=estate.id).count() == 1

    def test_estate_serializer_fields(self, estate):
        data = EstateSerializer(estate).data
        assert data["slug"] == estate.slug
        assert data["city"] == estate.city


@pytest.mark.django_db
class TestBlockAndUnit:
    def test_create_block(self, estate):
        block = Block.objects.create(estate=estate, name="Tower B", code="B")
        assert block.estate_id == estate.id

    def test_create_unit_with_unique_number_per_estate(self, estate, block):
        unit = Unit.objects.create(
            estate=estate,
            block=block,
            unit_number="B-202",
            monthly_service_charge=Decimal("75000.00"),
        )
        assert unit.occupancy_status == Unit.OccupancyStatus.VACANT
        assert str(unit) == f"{estate.slug}/B-202"

    def test_unit_serializer(self, unit):
        data = UnitSerializer(unit).data
        assert data["unit_number"] == "A-101"

    def test_unit_occupancy_transition(self, unit, user):
        unit.occupancy_status = Unit.OccupancyStatus.OCCUPIED
        unit.owner = user
        unit.save()
        unit.refresh_from_db()
        assert unit.occupancy_status == Unit.OccupancyStatus.OCCUPIED
        assert unit.owner_id == user.id


@pytest.mark.django_db
class TestTenancyMiddleware:
    def test_resolves_estate_from_header(self, estate):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/residents/", HTTP_X_ESTATE_ID=str(estate.id))

        def get_response(req):
            return type("Response", (), {"__setitem__": lambda s, k, v: None})()

        middleware = TenantMiddleware(get_response)
        middleware(request)
        assert request.estate_id == estate.id
        assert request.estate.slug == estate.slug

    def test_resolves_estate_from_slug_header(self, estate):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/residents/", HTTP_X_TENANT_SLUG=estate.slug)

        def get_response(req):
            return type("Response", (), {"__setitem__": lambda s, k, v: None})()

        middleware = TenantMiddleware(get_response)
        middleware(request)
        assert request.estate_id == estate.id

    def test_invalid_estate_id_raises_404(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/api/v1/residents/",
            HTTP_X_ESTATE_ID="00000000-0000-0000-0000-000000000099",
        )

        def get_response(req):
            return type("Response", (), {"__setitem__": lambda s, k, v: None})()

        middleware = TenantMiddleware(get_response)
        with pytest.raises(Http404):
            middleware(request)

    def test_auth_paths_exempt_from_tenant_resolution(self):
        factory = APIRequestFactory()
        request = factory.post("/api/v1/accounts/auth/token/")

        def get_response(req):
            return type("Response", (), {"__setitem__": lambda s, k, v: None})()

        middleware = TenantMiddleware(get_response)
        middleware(request)
        assert request.estate_id is None


@pytest.mark.django_db
class TestEstateViewSet:
    def test_list_active_estates(self, estate, admin_user, admin_role):
        from accounts.models import UserRole

        UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
        factory = APIRequestFactory()
        request = factory.get("/api/v1/estates/")
        force_authenticate(request, user=admin_user)
        view = EstateViewSet.as_view({"get": "list"})
        response = view(request)
        assert response.status_code == 200
        assert response.data["results"][0]["slug"] == estate.slug
