"""
Tests for importer forms.
"""
from __future__ import unicode_literals

import logging

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from ui.forms import UploadForm
from learningresources.tests.base import LoreTestCase

log = logging.getLogger(__name__)


class TestUploadForm(LoreTestCase):
    """Test the upload form."""

    def get_upload_file(self, ext):
        """Return an upload file to test the form."""
        filename = self.get_course_zip()
        return InMemoryUploadedFile(
            file=default_storage.open(filename, "rb"),
            field_name="course_file",
            name="toy{0}".format(ext),
            content_type="application/zip",
            size=default_storage.size(filename),
            charset="utf-8",
        )

    def test_init(self):
        """Get the form page."""
        form = UploadForm(
            {"repository": self.repo.id},
            {"course_file": self.get_upload_file(".zip")},
        )
        self.assertTrue(form.is_valid())
        form.save(self.user.id, self.repo.id, self.client.session)

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
            log.debug("checking extension %s", ext)
            self.assertEqual(validity, self.attempt_extension(ext))
            log.debug("it worked")

    def attempt_extension(self, ext):
        """Try to upload a file with a given extension."""
        upload = self.get_upload_file(ext)
        log.debug("attempt_extension %s, %s", ext, upload.name)
        form = UploadForm(
            {"repository": self.repo.id},
            {"course_file": upload},
        )
        is_valid = form.is_valid()
        log.debug("%s was valid: %s", upload.name, is_valid)
        return is_valid
