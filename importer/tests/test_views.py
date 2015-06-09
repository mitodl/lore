"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging

from django.core.files.storage import default_storage

from learningresources.models import LearningResource, Course
from learningresources.tests.base import LoreTestCase

from .test_import import get_course_zip

HTTP_OK = 200
UNAUTHORIZED = 403

log = logging.getLogger(__name__)


class TestViews(LoreTestCase):
    """Hit each view."""

    def test_upload_get(self):
        """GET upload page."""
        resp = self.client.get("/repositories/{0}/import".format(
            self.repo.slug), follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('enctype="multipart/form-data"' in body)

    def test_upload_get_bad_repo(self):
        """GET upload page."""
        resp = self.client.get("/repositories/999/import", follow=True)
        self.assertTrue(resp.status_code == UNAUTHORIZED)

    def test_upload_post(self):
        """POST upload page."""
        self.assertTrue(LearningResource.objects.count() == 0)
        body = self.upload_test_file()
        self.assertTrue(LearningResource.objects.count() == 5)
        # We should have been redirected to the Listing page.
        self.assertTrue('Listing</title>' in body)

    def test_upload_duplicate(self):
        """Gracefully inform the user."""
        self.assertTrue(Course.objects.count() == 0)
        self.upload_test_file()
        self.assertTrue(Course.objects.count() == 1)
        self.upload_test_file()
        self.assertTrue(Course.objects.count() == 1)

    def upload_test_file(self):
        """Used multiple times in tests"""
        with default_storage.open(get_course_zip(), "rb") as post_file:
            resp = self.client.post(
                "/repositories/{0}/import/".format(self.repo.slug),
                {"course_file": post_file, "repository": self.repo.id},
                follow=True
            )
        return resp.content.decode("utf-8")

    def test_invalid_form(self):
        """Upload invalid form"""
        resp = self.client.post(
            "/repositories/{0}/import/".format(self.repo.slug),
            {}, follow=True
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        log.debug(body)
        self.assertTrue("This field is required." in body)
