from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  # Default items per page
    page_query_param = "page"  # Query param to specify page (e.g., ?page=2)
    page_size_query_param = "size"  # Allow client to set page size via ?size=
    max_page_size = 100  # Max allowed page size
