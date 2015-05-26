"""
Test api functions.
"""

from __future__ import unicode_literals

from django.test.testcases import TestCase
from django.contrib.auth.models import User

from learningresources.models import Course
from learningresources.api import create_course


class TestCreateCourse(TestCase):
    """
    Test course creation API.
    """
    def setUp(self):
        """
        Set some test data
        """
        super(TestCreateCourse, self).setUp()
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
        super(TestCreateCourse, self).tearDown()
        kwargs = self.kwargs
        kwargs.pop("user_id")
        Course.objects.filter(**kwargs).delete()

    def test_create(self):
        """
        Create a course.
        """
        before = course_count()
        course = create_course(**self.kwargs)
        after = course_count()
        self.assertTrue(after == before + 1)
        self.assertTrue(course is not None)

        # Can't create a duplicate.
        with self.assertRaises(ValueError):
            create_course(**self.kwargs)
        self.assertTrue(course_count() == after)


def course_count():
    """
    Return number of courses in the database.
    """
    return Course.objects.count()
