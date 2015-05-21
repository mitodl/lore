"""
Tests for importer forms.
"""
from __future__ import unicode_literals

from os.path import getsize

from django.test.testcases import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from importer.forms import UploadForm

from .test_import import get_course_zip


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


class TestUploadForm(TestCase):
    """Test the upload form."""

    def setUp(self):
        """Initialize"""
        self.user, _ = User.objects.get_or_create(username="tester dude")

    def test_init(self):
        """Get the form page."""
        form = UploadForm({}, {"course_file": get_upload_file()})
        self.assertTrue(form.is_valid())
        form.save(self.user)
