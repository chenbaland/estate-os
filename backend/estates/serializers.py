from rest_framework import serializers

from core.serializers import TenantModelSerializer
from estates.models import Block, Estate, Unit


class PublicUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "unit_number", "unit_type", "floor", "bedrooms", "bathrooms"]


class PublicEstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = ["id", "name", "slug", "city", "state", "country"]


class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = [
            "id",
            "name",
            "slug",
            "estate_type",
            "tier",
            "description",
            "city",
            "state",
            "country",
            "timezone",
            "currency",
            "locale",
            "total_units",
            "occupied_units",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BlockSerializer(TenantModelSerializer):
    class Meta:
        model = Block
        fields = [
            "id",
            "estate",
            "name",
            "code",
            "description",
            "floor_count",
            "unit_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class UnitSerializer(TenantModelSerializer):
    class Meta:
        model = Unit
        fields = [
            "id",
            "estate",
            "block",
            "unit_number",
            "unit_type",
            "floor",
            "bedrooms",
            "bathrooms",
            "square_meters",
            "occupancy_status",
            "owner",
            "monthly_service_charge",
            "metadata",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
