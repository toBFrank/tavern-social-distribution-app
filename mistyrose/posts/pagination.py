# asked chatGPT how to paginate a list of objects with ListAPIView 2024-10-31
from rest_framework.pagination import PageNumberPagination

class LikesPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'size'  # Allow client to specify page size in the URL
    max_page_size = 100  # Max page size limit

class PostsPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'size'  # Allow client to specify page size in the URL
    max_page_size = 100  # Max page size limit


class CustomPostsPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'size'  # Allow the client to set page size
    max_page_size = 100  # Optional: maximum page size

    def get_paginated_response(self, data):
        return {
            "type": "posts",
            "page_number": self.page.number,
            "size": self.page.paginator.per_page,
            "count": self.page.paginator.count,
            "src": data,
        }