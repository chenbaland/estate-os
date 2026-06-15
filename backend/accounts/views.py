from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.auth_serializers import EmailTokenObtainPairSerializer
from accounts.membership import get_user_memberships
from accounts.models import Permission, Role, User
from accounts.serializers import PermissionSerializer, RoleSerializer, UserSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(
            {
                "user": UserSerializer(user).data,
                **get_user_memberships(user),
            }
        )

    def partial_update(self, request, *args, **kwargs):
        """PATCH /accounts/me/ — update editable profile fields only."""
        kwargs["partial"] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["code", "name", "module"]
    filterset_fields = ["module"]


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["code", "is_active"]

    def get_queryset(self):
        qs = Role.objects.filter(is_active=True)
        estate_id = getattr(self.request, "estate_id", None)
        if estate_id:
            qs = qs.filter(estate_id=estate_id)
        elif not self.request.user.is_superuser:
            qs = qs.none()
        return qs
