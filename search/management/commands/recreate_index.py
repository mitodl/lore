"""
Shell command to refresh the Elasticsearch index.
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from search.utils import recreate_index


class Command(BaseCommand):
    """
    Command for recreate_index.
    """
    help = "Clears the Elasticsearch index and recreates it."

    def handle(self, *args, **options):
        """Command for recreate_index"""
        recreate_index()
