"""
Signals handlers
"""
from __future__ import unicode_literals

import logging

from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from learningresources.models import Repository, repo_created
from roles.utils import sync_groups_permissions

log = logging.getLogger(__name__)


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


@receiver(post_save)
def add_creator_permission(sender, **kwargs):
    """
    Give the creator of a repository admin permissions
    over that repository.
    """
    from roles.api import assign_user_to_repo_group, roles_init_new_repo
    from roles.permissions import GroupTypes
    instance = kwargs.pop("instance", None)
    if not kwargs["created"]:
        return
    if not isinstance(instance, Repository):
        return
    roles_init_new_repo(instance)
    assign_user_to_repo_group(
        instance.created_by,
        instance,
        GroupTypes.REPO_ADMINISTRATOR,
    )
    # This signal is only fired upon initial creation of a repository,
    # so receivers don't have to check whether the repository is new.
    repo_created.send(sender=instance)
