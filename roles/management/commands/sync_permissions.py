"""
Shell command to synchronize permissions and apply the latest to all groups
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from roles.utils import sync_groups_permissions


class Command(BaseCommand):
    """
    Command for sync_permissions
    """
    help = "Synchronizes and updates permissions of the repository groups"

    def handle(self, *args, **options):
        """Command handler"""
        sync_groups_permissions()
