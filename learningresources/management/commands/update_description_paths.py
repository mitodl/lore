"""
Shell command to synchronize permissions and apply the latest to all groups
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import transaction

from learningresources.api import update_description_path
from learningresources.models import LearningResource


class Command(BaseCommand):
    """
    Command for sync_permissions
    """
    help = "Synchronizes and updates the description_path"

    def handle(self, *args, **options):
        """Command handler"""
        # updating the learning resources in the order they were
        # added to the database: this is  to process parents before children
        with transaction.atomic():
            all_learning_resources = LearningResource.objects.order_by('id')
            for learning_resource in all_learning_resources.iterator():
                update_description_path(learning_resource)
