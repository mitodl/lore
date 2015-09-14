"""
Pagination classes for Lore's REST API.
"""

from __future__ import unicode_literals

from rest_framework.pagination import PageNumberPagination


class LorePagination(PageNumberPagination):
    """
    Pagination class for Lore's REST API.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000
