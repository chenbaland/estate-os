from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import TenantViewSet
from maintenance.models import SLAConfig, Ticket, TicketComment
from maintenance.serializers import SLAConfigSerializer, TicketCommentSerializer, TicketSerializer


class SLAConfigViewSet(TenantViewSet):
    queryset = SLAConfig.objects.all()
    serializer_class = SLAConfigSerializer
    filterset_fields = ["priority", "category", "is_active"]
    search_fields = ["name", "category"]


class TicketViewSet(TenantViewSet):
    queryset = Ticket.objects.select_related("unit", "reported_by", "assigned_to")
    serializer_class = TicketSerializer
    filterset_fields = ["unit", "category", "priority", "status", "reported_by", "assigned_to"]
    search_fields = ["ticket_number", "title", "description"]

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            comments = ticket.comments.select_related("author").all()
            return Response(TicketCommentSerializer(comments, many=True).data)

        serializer = TicketCommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, author=request.user, estate_id=ticket.estate_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketCommentViewSet(TenantViewSet):
    queryset = TicketComment.objects.select_related("ticket", "author")
    serializer_class = TicketCommentSerializer
    filterset_fields = ["ticket", "author", "is_internal"]
    search_fields = ["body"]
