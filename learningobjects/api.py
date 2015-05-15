"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from datetime import datetime

from learningobjects.models import Course, Repository

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
    # TODO: Determine rules for accepting/requiring a repository.
    kwargs = {
        "org": org, "course_number": course_number, "semester": semester,
        "import_date": datetime.now(), 'imported_by_id': user_id,
        "repository_id": get_temp_repository(user_id).id
    }
    courses = Course.objects.filter(**kwargs)
    if courses.count() > 0:
        raise ValueError("Duplicate course")
    return Course.objects.create(**kwargs)

def get_temp_repository(user_id):
    """
    Use this for now so we can import *something*.
    """
    repos = Repository.objects.all()
    if repos.count() > 0:
        return repos[0]
    return Repository.objects.create(
        name="demo",
        create_date=datetime.now(),
        created_by_id=user_id,
    )
