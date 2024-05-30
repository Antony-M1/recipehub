from rest_framework.pagination import PageNumberPagination


RESPONSE_SUCSSS = {
    "status": "success",
    "message": "success",
    "data": {}
}

RESPONSE_FAILED = {
    "status": "failed",
    "message": "failed",
    "data": {}
}


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100