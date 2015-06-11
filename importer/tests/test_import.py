"""
Tests for LORE imports.
"""

from __future__ import unicode_literals

import os
from tempfile import mkstemp
import zipfile

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from importer.api import import_course_from_file
from importer.tasks import import_file
from learningresources.api import get_resources
from learningresources.models import Course
from learningresources.tests.base import LoreTestCase


class TestImportToy(LoreTestCase):
    """
    Test import functionality on an actual course. These tests should
    be expanded as needed to test regressions and handle valid but
    non-standard courses.
    """
    def setUp(self):
        """
        Return location of the local copy of the "simple" course for testing.
        """
        super(TestImportToy, self).setUp()
        self.course_zip = self.get_course_zip()
        self.bad_file = default_storage.save('bad_file', ContentFile(''))
        self.addCleanup(default_storage.delete, self.bad_file)

        # Valid zip file, wrong stuff in it.
        handle, bad_zip = mkstemp(suffix=".zip")
        os.close(handle)
        archive = zipfile.ZipFile(
            bad_zip, "w", compression=zipfile.ZIP_DEFLATED)
        archive.close()
        self.incompatible = default_storage.save(
            'bad_zip.zip', open(bad_zip, 'rb')
        )
        self.addCleanup(default_storage.delete, self.incompatible)

    def test_import_toy(self):
        """
        Simplest possible test.
        """
        self.assertTrue(get_resources(self.repo.id).count() == 0)
        self.assertTrue(Course.objects.count() == 0)
        import_course_from_file(self.course_zip, self.repo.id, self.user.id)
        self.assertTrue(get_resources(self.repo.id).count() == 5)
        self.assertTrue(Course.objects.count() == 1)

    def test_import_multiple(self):
        """
        Simplest possible test.
        """
        self.assertTrue(Course.objects.count() == 0)
        import_course_from_file(
            self.get_course_multiple_zip(), self.repo.id, self.user.id)
        self.assertTrue(Course.objects.count() == 2)

    def test_invalid_file(self):
        """Invalid zip file"""
        with self.assertRaises(ValueError) as ex:
            import_course_from_file(self.bad_file, self.repo.id, self.user.id)
        self.assertTrue(
            'Invalid OLX archive, unable to extract.' in ex.exception.args)

    def test_incompatible_file(self):
        """incompatible zip file (missing course structure)"""
        with self.assertRaises(ValueError) as ex:
            import_course_from_file(
                self.incompatible, self.repo.id, self.user.id)
        self.assertTrue(
            'Invalid OLX archive, no courses found.' in ex.exception.args)

    def test_import_single(self):
        """
        Single course (course.xml in root of archive).
        """
        self.assertTrue(Course.objects.count() == 0)
        import_course_from_file(
            self.get_course_single_tarball(), self.repo.id, self.user.id)
        self.assertTrue(Course.objects.count() == 1)

    def test_import_task(self):
        """
        Copy of test_import_single that just exercises tasks.py.
        """
        self.assertTrue(Course.objects.count() == 0)
        import_file(
            self.get_course_single_tarball(), self.repo.id, self.user.id)
        self.assertTrue(Course.objects.count() == 1)
