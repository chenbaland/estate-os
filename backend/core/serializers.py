from rest_framework import serializers


class EmptySerializer(serializers.Serializer):
    """Placeholder serializer for core endpoints."""

    pass


class TenantModelSerializer(serializers.ModelSerializer):
    """Serializer for tenant-scoped models with auto estate assignment."""

    estate = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        request = self.context.get("request")
        estate_id = getattr(request, "estate_id", None) if request else None
        if not estate_id:
            raise serializers.ValidationError({"detail": "X-Estate-Id header is required."})
        validated_data["estate_id"] = estate_id
        return super().create(validated_data)
