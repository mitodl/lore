"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from datetime import datetime

from learningresources.models import (
    Course, Repository, LearningResource, LearningResourceType
)

TYPE_LOOKUP = {}


def create_course(org, course_number, semester, user_id):
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
        "repository_id": get_temp_repository(user_id).id
    }
    if Course.objects.filter(**unique).exists():
        raise ValueError("Duplicate course")
    kwargs = {
        "org": org, "course_number": course_number, "semester": semester,
        'imported_by_id': user_id,
        "repository_id": get_temp_repository(user_id).id
    }
    course, _ = Course.objects.get_or_create(**kwargs)
    return course


def get_temp_repository(user_id):
    """
    Use this for now so we can import *something*.

    Args:
        user_id (int): primary key of user creating the course
    Returns:
        repository (learningresources.Repository): repository
    """
    repos = Repository.objects.all()
    if repos.count() > 0:
        return repos[0]
    return Repository.objects.create(
        name="demo",
        create_date=datetime.now(),
        created_by_id=user_id,
    )


def create_lox(kwargs):
    """
    Create a learning resource.

    Args:
        course (learningresources.Course): course
        parent (learningresources.LearningResource): parent LearningResource
        lox_type (unicode): name of LearningResourceType
        title (unicode): title of resource
        content_xml (unicode): XML
        mpath (unicode): materialized path
    Returns:
        lox (learningresources.LearningResource): new LearningResource
    """
    params = {
        "course": kwargs["course"],
        "learning_resource_type_id": type_id_by_name(kwargs["lox_type"]),
        "title": kwargs["title"],
        "content_xml": kwargs["content_xml"],
        "materialized_path": kwargs["mpath"],
    }
    if kwargs["parent"] is not None:
        params["parent_id"] = kwargs["parent"].id
    lox = LearningResource(**params)
    lox.save()
    return lox


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
    obj, _ = LearningResourceType.objects.get_or_create(name=name.lower())
    TYPE_LOOKUP[name] = obj.id
    return obj.id
