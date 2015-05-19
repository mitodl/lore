"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from datetime import datetime

from learningobjects.models import (
    Course, Repository, LearningObject, LearningObjectType
)

TYPE_LOOKUP = {}

# pylint: disable=no-member


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
        repository (learningobjects.Repository): repository
    """
    repos = Repository.objects.all()
    if repos.count() > 0:
        return repos[0]
    return Repository.objects.create(
        name="demo",
        create_date=datetime.now(),
        created_by_id=user_id,
    )


def create_lox(course, parent, lox_type, title, content_xml):
    """
    Create a learning object.

    Args:
        course (learningobjects.Course): course
        parent (learningobjects.LearningObject): parent LearningObject
    Returns:
        lox (learningobjects.LearningObject): newly-created LearningObject
    """

    lox = LearningObject(
        course=course,
        parent_id=parent.id if parent is not None else None,
        learning_object_type_id=type_id_by_name(lox_type),
        title=title,
        content_xml=content_xml,
    )
    lox.save()
    return lox


def type_id_by_name(name):
    """
    Get or create a LearningObjectType by name.

    This would do fewer queries if it did all the lookups up front, but
    this is simpler to read and understand and still prevents most lookups.
    Also, it can't prevent inserts, so it's never guaranteed to be just
    a single query.

    Args:
        name (unicode): LearningObjectType.name
    Returns:
        type_id (int): pk of learningobjects.LearningObjectType
    """
    if name in TYPE_LOOKUP:
        return TYPE_LOOKUP[name]
    obj, _ = LearningObjectType.objects.get_or_create(name=name.lower())
    TYPE_LOOKUP[name] = obj.id
    return obj.id
