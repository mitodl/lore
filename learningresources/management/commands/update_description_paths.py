"""
Shell command to synchronize permissions and apply the latest to all groups
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from learningresources.api import update_description_path
from learningresources.models import LearningResource


class Command(BaseCommand):
    """
    Command for sync_permissions
    """
    help = "Synchronizes and updates the description_path"

    def handle(self, *args, **options):
        """Command handler"""
        for learning_resource in LearningResource.objects.all():
            update_description_path(learning_resource)
