"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from __future__ import unicode_literals

from django.db import transaction

from learningresources.models import (
    Course, Repository, LearningResource, LearningResourceType
)

TYPE_LOOKUP = {}


def create_course(org, repo_id, course_number, semester, user_id):
    """
    Add a course to the database.
    Args:
        org (unicode): organization
        course_number (unicode): course number
        semester (unicode): semester
        user_id (int): primary key of user creating the course
    Raises:
        ValueError: Duplicate course
    Returns: None
    """
    # Check on unique values before attempting a get_or_create, because
    # items such as import_date will always make it non-unique.
    unique = {
        "org": org, "course_number": course_number, "semester": semester,
        "repository_id": repo_id,
    }
    if Course.objects.filter(**unique).exists():
        raise ValueError("Duplicate course")
    kwargs = {
        "org": org, "course_number": course_number, "semester": semester,
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
        course (learningresources.Course): course
        parent (learningresources.LearningResource): parent LearningResource
        resource_type (unicode): name of LearningResourceType
        title (unicode): title of resource
        content_xml (unicode): XML
        mpath (unicode): materialized path
    Returns:
        resource (learningresources.LearningResource): new LearningResource
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
        type_id (int): pk of learningresources.LearningResourceType
    """
    if name in TYPE_LOOKUP:
        return TYPE_LOOKUP[name]
    with transaction.atomic():
        obj, _ = LearningResourceType.objects.get_or_create(name=name.lower())
    TYPE_LOOKUP[name] = obj.id
    return obj.id


def get_repos(user_id):
    """
    Get all repositories a user may see.

    Args:
        user (auth.User): request.user
    Returns:
        repos query set of learningresource.Repository: repositories
    """
    return Repository.objects.filter(created_by__id=user_id).order_by('name')


def get_repo_courses(repo_id):
    """
    Get courses for a repository.
    Args:
        repository (int): pk of learningresource.Repository
    Returns:
        courses (queryset of learningresource.Course): courses
    """
    return Course.objects.filter(repository__id=repo_id)


def create_repo(name, description, user_id):
    """
    Create a new repository.
    Args:
        name (unicode): repository name
        description (unicode): repository description
        user_id (int): user ID of repository creator
    Returns:
        repo (learningresources.Repository): newly-created repo
    """
    with transaction.atomic():
        return Repository.objects.create(
            name=name, description=description,
            created_by_id=user_id,
        )


def get_user_courses(user_id):
    """
    Get all user's courses.
    Args:
        user_id (int): primary key of user
    Returns:
        Queryset of learningresources.Course: courses
    """
    repo_ids = [x.id for x in get_repos(user_id)]
    return Course.objects.filter(repository_id__in=repo_ids)


def get_semesters(user_id):
    """
    Get semesters in all user's courses.
    Args:
        user_id (int): primary key of user
    Returns:
        semesters (list of strings): semester names
    """
    courses = get_user_courses(user_id)
    return sorted(list(set([x.semester for x in courses])))
