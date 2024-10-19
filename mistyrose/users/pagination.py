# asked chatGPT how to paginate a list of objects with ListAPIView 2024-10-18
from rest_framework.pagination import PageNumberPagination

class AuthorsPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'size'  # Allow client to specify page size in the URL
    max_page_size = 100  # Max page size limit
