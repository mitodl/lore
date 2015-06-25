"""
Functions for handling roles
"""

from __future__ import unicode_literals

from django.contrib.auth.models import Group, Permission
from django.db import transaction
from guardian.shortcuts import assign_perm, get_perms, remove_perm

from roles.permissions import (
    RepoPermission, GroupTypes, BaseGroupTypes, InvalidGroupType
)
from roles.user_models import UserGroup


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


def list_users_in_repo(repo, base_group_type=None):
    """
    Lists all the users in the repository groups
    If the group type is specified, the list is limited to that group

    Args:
        repo (learningresources.models.Repository): repository used to extract
            the right group to use
        base_group_type (unicode): group type from
            roles.permissions.BaseGroupTypes
    Returns:
        list (list of roles.user_models.UserGroup): list of users in one or
            all the repository groups
    """
    users_groups = []
    if base_group_type is not None:
        if not BaseGroupTypes.is_base_group_type(base_group_type):
            raise InvalidGroupType
        base_group_types = [base_group_type]
    else:
        base_group_types = BaseGroupTypes.all_base_groups()
    for base_group_type in base_group_types:
        group = Group.objects.get(
            name=GroupTypes.get_repo_groupname_by_base(
                base_group_type
            ).format(repo.slug)
        )
        users_groups += [
            UserGroup(user.username, base_group_type)
            for user in group.user_set.all()
        ]
    return users_groups


def is_last_admin_in_repo(user, repo):
    """
    Checks if user is the last administrator in the repository.
    It does not check if the user is an actual administrator and in that case
    it will simply return False

    Args:
        user (django.contrib.auth.models.User): user
        repo (learningresources.models.Repository): repository used to extract
            the right group to use
    Returns:
        bool
    """
    admins_in_repo = list_users_in_repo(
        repo,
        base_group_type=BaseGroupTypes.ADMINISTRATORS
    )
    return (
        UserGroup(
            user.username,
            BaseGroupTypes.ADMINISTRATORS
        ) in admins_in_repo
    ) and len(admins_in_repo) == 1
