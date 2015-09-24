"""
Shell command to refresh the Elasticsearch index.
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from search.utils import clear_index, create_mapping


class Command(BaseCommand):
    """
    Command for sync_permissions
    """
    help = "Refreshes the Elasticsearch index."

    def handle(self, *args, **options):
        """Command handler"""
        clear_index()
        create_mapping()
