"""
Shell command to refresh the Elasticsearch index.
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from learningresources.models import LearningResource
from search.utils import index_resources, create_mapping


class Command(BaseCommand):
    """
    Command for refresh_index
    """
    help = "Updates the Elasticsearch index and mapping."

    def handle(self, *args, **options):
        """Refreshes the Elasticsearch index."""
        create_mapping()
        index_resources(LearningResource.objects.all())
