"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User
from django.db import transaction

from guardian.shortcuts import get_objects_for_user, get_perms

from learningresources.models import (
    Course, Repository, LearningResource, LearningResourceType
)
from roles.permissions import RepoPermission

log = logging.getLogger(__name__)


class LearningResourceException(Exception):
    """Base class for our custom exceptions."""
    pass


class PermissionDenied(LearningResourceException):
    """
    Raised by the API when the requested item exists, but the
    user is not allowed to access it.
    """
    pass


class NotFound(LearningResourceException):
    """Raised by the API when the item requested does not exist."""
    pass


def create_course(org, repo_id, course_number, run, user_id):
    """
    Add a course to the database.

    Args:
        org (unicode): Organization
        course_number (unicode): Course number
        run (unicode): Run
        user_id (int): Primary key of user creating the course
    Raises:
        ValueError: Duplicate course
    Returns:
        course (learningresource.Course): The created course

    """
    # Check on unique values before attempting a get_or_create, because
    # items such as import_date will always make it non-unique.
    unique = {
        "org": org, "course_number": course_number, "run": run,
        "repository_id": repo_id,
    }
    if Course.objects.filter(**unique).exists():
        raise ValueError("Duplicate course")
    kwargs = {
        "org": org, "course_number": course_number, "run": run,
        'imported_by_id': user_id,
        "repository_id": repo_id,
    }
    with transaction.atomic():
        course, _ = Course.objects.get_or_create(**kwargs)
    return course


# pylint: disable=too-many-arguments
def create_resource(course, parent, resource_type, title, content_xml, mpath):
    """
    Create a learning resource.

    Args:
        course (learningresources.Course): Course
        parent (learningresources.LearningResource): Parent LearningResource
        resource_type (unicode): Name of LearningResourceType
        title (unicode): Title of resource
        content_xml (unicode): XML
        mpath (unicode): Materialized path

    Returns:
        resource (learningresources.LearningResource): New LearningResource
    """
    params = {
        "course": course,
        "learning_resource_type_id": type_id_by_name(resource_type),
        "title": title,
        "content_xml": content_xml,
        "materialized_path": mpath,
    }
    if parent is not None:
        params["parent_id"] = parent.id
    with transaction.atomic():
        return LearningResource.objects.create(**params)


def type_id_by_name(name):
    """
    Get or create a LearningResourceType by name.

    This would do fewer queries if it did all the lookups up front, but
    this is simpler to read and understand and still prevents most lookups.
    Also, it can't prevent inserts, so it's never guaranteed to be just
    a single query.

    Args:
        name (unicode): LearningResourceType.name
    Returns:
        type_id (int): Primary key of learningresources.LearningResourceType
    """
    with transaction.atomic():
        obj, _ = LearningResourceType.objects.get_or_create(name=name.lower())
        return obj.id


def get_repos(user_id):
    """
    Get all repositories a user may access.

    Args:
        user_id (int): Primary key of user
    Returns:
        repos (query set of learningresource.Repository): Repositories
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise PermissionDenied(
            "user does not have permission for this repository"
        )
    return get_objects_for_user(
        user,
        RepoPermission.view_repo[0],
        klass=Repository
    )


def get_repo(repo_slug, user_id):
    """
    Get repository for a user if s/he can access it.
    Returns a repository object if it exists or
    * raises a 404 if the object does not exist
    * raises a 403 if the object exists but the user doesn't have permission

    Args:
        repo_slug (unicode): Repository slug
        user_id (int): Primary key of user
    Returns:
        repo (learningresource.Repository): Repository
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise PermissionDenied(
            "user does not have permission for this repository")
    try:
        repo = Repository.objects.get(slug=repo_slug)
    except Repository.DoesNotExist:
        raise NotFound()

    if RepoPermission.view_repo[0] in get_perms(user, repo):
        return repo
    raise PermissionDenied("user does not have permission for this repository")


def create_repo(name, description, user_id):
    """
    Create a new repository.

    Args:
        name (unicode): Repository name
        description (unicode): Repository description
        user_id (int): User ID of repository creator
    Returns:
        repo (learningresources.Repository): Newly-created repository
    """
    with transaction.atomic():
        return Repository.objects.create(
            name=name, description=description,
            created_by_id=user_id,
        )


def get_resources(repo_id):
    """
    Get resources from a repository ordered by title.

    Args:
        repo_id (int): Primary key of the repository
    Returns:
        list (list of learningresources.LearningResource): List of resources
    """
    return LearningResource.objects.select_related(
        "learning_resource_type").filter(
            course__repository__id=repo_id).order_by("title")


def get_resource(resource_id, user_id):
    """
    Get single resource.

    Args:
        resource_id (int): Primary key of the LearningResource
        user_id (int): Primary key of the user requesting the resource
    Returns:
        resource (learningresources.LearningResource): Resource
            May be None if the resource does not exist or the user does
            not have permissions.
    """
    try:
        resource = LearningResource.objects.get(id=resource_id)
    except LearningResource.DoesNotExist:
        raise NotFound("LearningResource not found")
    # This will raise PermissionDenied if it fails.
    get_repo(resource.course.repository.slug, user_id)
    return resource
