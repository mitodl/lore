"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseForbidden

from guardian.shortcuts import get_objects_for_user, get_perms

from learningresources.models import (
    Course, Repository, LearningResource, LearningResourceType
)
from roles.permissions import RepoPermission

TYPE_LOOKUP = {}

log = logging.getLogger(__name__)


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
    if name in TYPE_LOOKUP:
        return TYPE_LOOKUP[name]
    with transaction.atomic():
        obj, _ = LearningResourceType.objects.get_or_create(name=name.lower())
    TYPE_LOOKUP[name] = obj.id
    return obj.id


def get_repos(user_id):
    """
    Get all repositories a user may access.

    Args:
        user_id (int): Primary key of user
    Returns:
        repos (query set of learningresource.Repository): Repositories
    """
    user = User.objects.get(id=user_id)
    return get_objects_for_user(
        user,
        RepoPermission.view_repo[0],
        klass=Repository
    )


def get_repo_or_error(repo_slug, user_id):
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
    user = User.objects.get(id=user_id)
    repo = get_object_or_404(Repository, slug=repo_slug)
    if RepoPermission.view_repo[0] in get_perms(user, repo):
        return repo
    raise PermissionDenied()


def get_repo_courses(repo_id):
    """
    Get courses for a repository.

    Args:
        repo_id (int): Primary key of learningresource.Repository
    Returns:
        courses (queryset of learningresource.Course): Courses
    """
    return Course.objects.filter(repository__id=repo_id)


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


def get_courses(repo_id):
    """
    Get all user's courses.

    Args:
        repo_id (int): Primary key of the repository
    Returns:
        courses (Queryset of learningresources.Course): User's courses
    """
    return Course.objects.filter(repository_id=repo_id)


def get_runs(repo_id):
    """
    Get runs in all user's courses for the repo.

    The list of runs is sorted.

    Args:
        repo_id (int): Primary key of the repository
    Returns:
        runs (list of strings): Run names
    """
    courses = get_courses(repo_id)
    return sorted(list(set([x.run for x in courses])))


def get_user_tags(repo_id):
    """
    Get all tags for a user's courses.

    Args:
        repo_id (int): Primary key of the repository
    Returns:
        tags (list of strings): Tag names
    """
    resources = LearningResource.objects.filter(course__repository__id=repo_id)
    tag_ids = set([x.learning_resource_type_id for x in resources])
    stuff = LearningResourceType.objects.filter(id__in=tag_ids).order_by(
        "name")
    return stuff


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
    """
    resource = get_object_or_404(LearningResource, id=resource_id)
    if has_repo(resource.course.repository_id, user_id):
        return resource
    return HttpResponseForbidden


def has_repo(repo_id, user_id):
    """
    Can a user access a repository?

    Returns ``True`` if a user can view a repository,
    ``False`` if they can not.

    Args:
        repo_id (int): Primary key of the repository
        user_id (int): Primary key of the user
    Returns:
        bool: If user is allowed to access the repository.
    """
    repos = get_repos(user_id)
    return repo_id in set([x.id for x in repos])
