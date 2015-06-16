"""
Utility functions for roles
"""
from __future__ import unicode_literals

from learningresources.models import Repository
from roles.api import roles_init_new_repo, roles_clear_repo_permissions


def sync_groups_permissions():
    """
    Synchronize latest permissions and applies them to all
    existing group repositories

    Args:
        None
    Returns:
        None
    """
    for repo in Repository.objects.all():
        # this needs to be idempotent
        roles_clear_repo_permissions(repo)
        roles_init_new_repo(repo)
