from rest_framework.pagination import PageNumberPagination


class CustomNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"
    max_page_size = 100
