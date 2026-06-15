from rest_framework.pagination import CursorPagination


class EstateCursorPagination(CursorPagination):
    """Cursor-based pagination for large estate-scoped datasets."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"
    cursor_query_param = "cursor"
