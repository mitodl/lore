"""
Signals handlers
"""
from __future__ import unicode_literals

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from learningresources.models import Repository
from roles.utils import sync_groups_permissions


# pylint: disable=unused-argument
@receiver(post_migrate)
def my_callback(sender, **kwargs):
    """
    Signal handler to apply new permissions to repositories
    only in case the sender is learningresources.
    """
    # pylint: disable=protected-access
    if sender.name == Repository._meta.app_label:
        sync_groups_permissions()
