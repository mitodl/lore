"""
Tests for importer forms.
"""
from __future__ import unicode_literals

from os.path import getsize
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile

from ui.forms import UploadForm
from learningresources.tests.base import LoreTestCase

from .test_import import get_course_zip

log = logging.getLogger(__name__)


def get_upload_file(ext):
    """Return an upload file to test the form."""
    filename = get_course_zip()
    return InMemoryUploadedFile(
        file=open(filename, "rb"),
        field_name="course_file",
        name="toy{0}".format(ext),
        content_type="application/zip", size=getsize(filename),
        charset="utf-8",
    )


class TestUploadForm(LoreTestCase):
    """Test the upload form."""

    def test_init(self):
        """Get the form page."""
        form = UploadForm(
            {"repository": self.repo.id},
            {"course_file": get_upload_file(".zip")},
        )
        self.assertTrue(form.is_valid())
        form.save(self.user.id, self.repo.id)

    def test_extensions(self):
        """Only certain extensions are valid."""
        checks = (
            (".zip", True),
            (".tar.gz", True),
            (".tgz", True),
            (".foo", False),
            (".jpg", False),
        )
        for ext, validity in checks:
            self.assertEqual(validity, self.attempt_extension(ext))

    def attempt_extension(self, ext):
        """Try to upload a file with a given extension."""
        upload = get_upload_file(ext)
        form = UploadForm(
            {"repository": self.repo.id},
            {"course_file": upload},
        )
        is_valid = form.is_valid()
        return is_valid
