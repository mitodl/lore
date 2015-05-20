"""
Tests for LORE imports.
"""

import os
from os.path import abspath, dirname, join
from tempfile import mkstemp

from django.test.testcases import TestCase
from django.contrib.auth.models import User

from importer.api import import_course_from_file
from learningobjects.models import LearningObject


def get_course_zip():
    """
    Get the path to the demo course.
    Returns:
        path (unicode): absolute path to zip file
    """
    path = join(abspath(dirname(__file__)), "testdata", "courses")
    return join(path, "two_toys.zip")


class TestImportToy(TestCase):
    """
    Test import functionality on an actual course. These tests should
    be expanded as needed to test regressions and handle valid but
    non-standard courses.
    """
    def setUp(self):
        """
        Return location of the local copy of the "two_toys"
        course for testing.
        for testing.
        """
        super(TestImportToy, self).setUp()
        self.user, _ = User.objects.get_or_create(username="test")
        self.course_zip = get_course_zip()
        handle, self.bad_file = mkstemp()
        os.close(handle)

    def tearDown(self):
        """clean up"""
        super(TestImportToy, self).tearDown()
        os.remove(self.bad_file)

    def test_import_toy(self):
        """
        Simplest possible test.
        """
        self.assertTrue(LearningObject.objects.count() == 0)
        import_course_from_file(self.course_zip, self.user.id)
        self.assertTrue(LearningObject.objects.count() == 5)

    def test_bad_file(self):
        """Invalid zip file"""
        self.assertTrue(LearningObject.objects.count() == 0)
        with self.assertRaises(ValueError):
            import_course_from_file(self.bad_file, self.user.id)
        self.assertTrue(LearningObject.objects.count() == 0)
