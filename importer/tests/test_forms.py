"""
Tests for importer forms.
"""
from __future__ import unicode_literals

from os.path import getsize
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile

from importer.forms import UploadForm
from learningresources.tests.base import LoreTestCase

from .test_import import get_course_zip

log = logging.getLogger(__name__)


def get_upload_file():
    """Return a usable upload file to test the form."""
    filename = get_course_zip()
    return InMemoryUploadedFile(
        file=open(filename, "rb"),
        field_name="course_file",
        name="toy.zip",
        content_type="application/zip", size=getsize(filename),
        charset="utf-8",
    )


class TestUploadForm(LoreTestCase):
    """Test the upload form."""

    def test_init(self):
        """Get the form page."""
        form = UploadForm(
            {"repository": self.repo.id},
            {"course_file": get_upload_file()},
        )
        self.assertTrue(form.is_valid())
        form.save(self.user)
