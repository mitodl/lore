"""
Tests for LORE imports.
"""

from __future__ import unicode_literals

import os
from os.path import abspath, dirname, join
from tempfile import mkstemp
from shutil import copyfile
import zipfile

from importer.api import import_course_from_file
from learningresources.models import LearningResource, Course
from learningresources.tests.base import LoreTestCase


def get_course_zip():
    """
    Get the path to the demo course. Creates a copy, because the
    importer deletes the file during cleanup.

    Returns:
        path (unicode): absolute path to zip file
    """
    path = join(abspath(dirname(__file__)), "testdata", "courses")
    handle, filename = mkstemp(suffix=".zip")
    os.close(handle)
    copyfile(join(path, "two_toys.zip"), filename)
    return filename

def get_course_multiple_zip():
    """
    Get the path to the demo course. Creates a copy, because the
    importer deletes the file during cleanup.

    Returns:
        path (unicode): absolute path to zip file
    """
    path = join(abspath(dirname(__file__)), "testdata", "courses")
    handle, filename = mkstemp(suffix=".tar.gz")
    os.close(handle)
    copyfile(join(path, "test-two-courses.tar.gz"), filename)
    return filename

class TestImportToy(LoreTestCase):
    """
    Test import functionality on an actual course. These tests should
    be expanded as needed to test regressions and handle valid but
    non-standard courses.
    """
    def setUp(self):
        """
        Return location of the local copy of the "two_toys" course for testing.
        """
        super(TestImportToy, self).setUp()
        self.course_zip = get_course_zip()
        handle, self.bad_file = mkstemp()
        os.close(handle)

        # Valid zip file, wrong stuff in it.
        handle, self.incompatible = mkstemp(suffix=".zip")
        os.close(handle)
        archive = zipfile.ZipFile(
            self.incompatible, "w", compression=zipfile.ZIP_DEFLATED)
        archive.close()

    def test_import_toy(self):
        """
        Simplest possible test.
        """
        self.assertTrue(LearningResource.objects.count() == 0)
        self.assertTrue(Course.objects.count() == 0)
        import_course_from_file(self.course_zip, self.repo.id, self.user.id)
        self.assertTrue(LearningResource.objects.count() == 5)
        self.assertTrue(Course.objects.count() == 1)

    def test_import_multiple(self):
        """
        Simplest possible test.
        """
        self.assertTrue(Course.objects.count() == 0)
        import_course_from_file(get_course_multiple_zip(), self.user.id)
        self.assertTrue(Course.objects.count() == 2)

    def test_invalid_file(self):
        """Invalid zip file"""
        try:
            import_course_from_file(self.bad_file, self.user.id)
        except ValueError as ex:
            self.assertTrue('Invalid OLX archive, unable to extract' in ex.args)
        raise ValueError("shouldn't happen")

    def test_incompatible_file(self):
        """incompatible zip file (missing course structure)"""
        try:
            import_course_from_file(self.incompatible, self.user.id)
        except ValueError as ex:
            self.assertTrue('Invalid OLX archive, no courses found' in ex.args)
        raise ValueError("shouldn't happen")
