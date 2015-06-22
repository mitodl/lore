"""
Functions for handling roles
"""

from __future__ import unicode_literals

from django.contrib.auth.models import Group, Permission
from django.db import transaction
from guardian.shortcuts import assign_perm, get_perms, remove_perm

from roles.permissions import RepoPermission, GroupTypes


def roles_init_new_repo(repo):
    """
    Create new groups for the repository

    It assumes that there are only 3 types of users:
        - administrator
        - curator
        - author

    Args:
        repo (learningresources.models.Repository): repository used to create
            groups and assign permissions to them
    Returns:
        None
    """
    with transaction.atomic():
        administrator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_ADMINISTRATOR.format(repo.slug)
        )
        curator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_CURATOR.format(repo.slug)
        )
        author_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_AUTHOR.format(repo.slug)
        )

    with transaction.atomic():
        # administrator permissions
        for permission in RepoPermission.administrator_permissions():
            try:
                Permission.objects.get(codename=permission)
                assign_perm(permission, administrator_group, repo)
            except Permission.DoesNotExist:
                pass
        # curator permissions
        for permission in RepoPermission.curator_permissions():
            try:
                Permission.objects.get(codename=permission)
                assign_perm(permission, curator_group, repo)
            except Permission.DoesNotExist:
                pass
        # author permissions
        for permission in RepoPermission.author_permissions():
            try:
                Permission.objects.get(codename=permission)
                assign_perm(permission, author_group, repo)
            except Permission.DoesNotExist:
                pass


def roles_clear_repo_permissions(repo):
    """
    Removes all the permissions a group has on a repo
    Args:
        repo (learningresources.models.Repository): repository
    Returns:
        None
    """
    with transaction.atomic():
        administrator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_ADMINISTRATOR.format(repo.slug)
        )
        curator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_CURATOR.format(repo.slug)
        )
        author_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_AUTHOR.format(repo.slug)
        )
        all_groups = [administrator_group, curator_group, author_group]
        for group in all_groups:
            perms = get_perms(group, repo)
            for perm in perms:
                remove_perm(perm, group, repo)


def roles_update_repo(repo, old_slug):
    """
    Updates the groups names for the repo

    Args:
        repo (learningresources.models.Repository): repository used to update
            groups and assign permissions to them
        old_slug (unicode): old slug string used to retrieve the groups that
            need to be renamed
    Returns:
        None
    """
    # if the slug has not changed there is nothing to do
    if repo.slug == old_slug:
        return
    with transaction.atomic():
        administrator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_ADMINISTRATOR.format(old_slug)
        )
        curator_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_CURATOR.format(old_slug)
        )
        author_group, _ = Group.objects.get_or_create(
            name=GroupTypes.REPO_AUTHOR.format(old_slug)
        )
    administrator_group.name = GroupTypes.REPO_ADMINISTRATOR.format(repo.slug)
    curator_group.name = GroupTypes.REPO_CURATOR.format(repo.slug)
    author_group.name = GroupTypes.REPO_AUTHOR.format(repo.slug)
    with transaction.atomic():
        administrator_group.save()
        curator_group.save()
        author_group.save()


def assign_user_to_repo_group(
        user,
        repo,
        group_type):
    """
    Assigns an user to a repo specific group type

    Args:
        user (django.contrib.auth.models.User): user
        repo (learningresources.models.Repository): repository used to extract
            the right group to use
        group_type (roles.permissions.GroupTypes): group string to be used to
            construct the group name
    Returns:
        None
    """
    with transaction.atomic():
        repo_group = Group.objects.get(name=group_type.format(repo.slug))
        user.groups.add(repo_group)
        user.save()


def remove_user_from_repo_group(
        user,
        repo,
        group_type):
    """
    Remove an user to from a repo specific group type

    Args:
        user (django.contrib.auth.models.User): user
        repo (learningresources.models.Repository): repository used to extract
            the right group to use
        group_type (roles.permissions.GroupTypes): group string to be used to
            construct the group name
    Returns:
        None
    """
    with transaction.atomic():
        repo_group = Group.objects.get(name=group_type.format(repo.slug))
        user.groups.remove(repo_group)
        user.save()
