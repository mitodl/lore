"""
Test api functions.
"""

from django.test.testcases import TestCase

from django.contrib.auth.models import User

from learningobjects.models import Course
from learningobjects.api import create_course

# pylint: disable=no-member


class TestCreateCourse(TestCase):
    """
    Test course creation API.
    """
    def setUp(self):
        """
        Set some test data
        """
        self.user, _ = User.objects.get_or_create(username="test")
        self.kwargs = {
            'org': 'demo org',
            'course_number': '42',
            'semester': 'Febtober',
            'user_id': self.user.id,
        }

    def tearDown(self):
        """
        Clean up test data.
        """
        kwargs = self.kwargs
        kwargs.pop("user_id")
        Course.objects.filter(**kwargs).delete()

    def test_create(self):
        """
        Create a course.
        """
        before = course_count()
        create_course(**self.kwargs)
        self.assertTrue(course_count() == before + 1)

    def test_create_dupe(self):
        """
        Can't create a duplicate.
        """
        before = course_count()
        create_course(**self.kwargs)
        create_course(**self.kwargs)
        self.assertTrue(course_count() == before + 1)


def course_count():
    """
    Return number of courses in the database.
    """
    return Course.objects.count()
