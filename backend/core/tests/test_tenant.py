"""Tenant middleware isolation tests."""
import pytest
from django.http import Http404
from django.test import RequestFactory

from core.middleware.tenant import TenantMiddleware
from estates.models import Estate


@pytest.mark.django_db
class TestTenantIsolation:
    def test_each_request_scoped_to_single_estate(self, estate, other_estate):
        factory = RequestFactory()

        def get_response(request):
            class Response:
                def __setitem__(self, key, value):
                    pass

            return Response()

        middleware = TenantMiddleware(get_response)

        request_a = factory.get("/api/v1/billing/", HTTP_X_ESTATE_ID=str(estate.id))
        middleware(request_a)
        assert request_a.estate_id == estate.id

        request_b = factory.get("/api/v1/billing/", HTTP_X_ESTATE_ID=str(other_estate.id))
        middleware(request_b)
        assert request_b.estate_id == other_estate.id
        assert request_a.estate_id != request_b.estate_id

    def test_inactive_estate_not_resolved(self, estate):
        estate.is_active = False
        estate.save()
        factory = RequestFactory()
        request = factory.get("/api/v1/residents/", HTTP_X_ESTATE_ID=str(estate.id))

        def get_response(req):
            class Response:
                def __setitem__(self, key, value):
                    pass

            return Response()

        middleware = TenantMiddleware(get_response)
        with pytest.raises(Http404):
            middleware(request)

    def test_deleted_estate_not_resolved(self, estate):
        estate.soft_delete()
        factory = RequestFactory()
        request = factory.get("/api/v1/residents/", HTTP_X_ESTATE_ID=str(estate.id))

        def get_response(req):
            class Response:
                def __setitem__(self, key, value):
                    pass

            return Response()

        middleware = TenantMiddleware(get_response)
        with pytest.raises(Http404):
            middleware(request)

    def test_response_includes_estate_header(self, estate):
        factory = RequestFactory()
        request = factory.get("/api/v1/residents/", HTTP_X_ESTATE_ID=str(estate.id))

        def get_response(req):
            class Response(dict):
                pass

            return Response()

        middleware = TenantMiddleware(get_response)
        response = middleware(request)
        assert response["X-Estate-Id"] == str(estate.id)

    def test_health_endpoint_exempt(self):
        factory = RequestFactory()
        request = factory.get("/health/")

        def get_response(req):
            class Response:
                def __setitem__(self, key, value):
                    pass

            return Response()

        middleware = TenantMiddleware(get_response)
        middleware(request)
        assert request.estate_id is None
