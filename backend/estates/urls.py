from django.urls import path
from rest_framework.routers import DefaultRouter

from estates.views import BlockViewSet, EstateViewSet, PublicEstateListView, PublicEstateUnitsView, UnitViewSet

router = DefaultRouter()
router.register(r"estates", EstateViewSet, basename="estate")
router.register(r"blocks", BlockViewSet, basename="block")
router.register(r"units", UnitViewSet, basename="unit")

urlpatterns = [
    path("public/", PublicEstateListView.as_view(), name="estate-public-list"),
    path("public/<uuid:estate_id>/units/", PublicEstateUnitsView.as_view(), name="estate-public-units"),
    *router.urls,
]
