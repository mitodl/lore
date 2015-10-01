"""
Shell command to refresh the Elasticsearch index.
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from learningresources.models import LearningResource
from search.utils import index_resources


class Command(BaseCommand):
    """
    Command for sync_permissions
    """
    help = "Refreshes the Elasticsearch index."

    def handle(self, *args, **options):
        """Command handler"""
        index_resources(LearningResource.objects.all())
