"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging

from learningresources.models import LearningResource, Course
from learningresources.tests.base import LoreTestCase

from .test_import import get_course_zip

HTTP_OK = 200
UNAUTHORIZED = 403

log = logging.getLogger(__name__)


class TestViews(LoreTestCase):
    """Hit each view."""

    def test_status_get(self):
        """Status page."""
        resp = self.client.get("/importer/status", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("Number of learning resources:" in body)

    def test_upload_get(self):
        """GET upload page."""
        resp = self.client.get("/importer/upload/{0}".format(
            self.repo.id), follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('enctype="multipart/form-data"' in body)

    def test_upload_get_bad_repo(self):
        """GET upload page."""
        resp = self.client.get("/importer/upload/999", follow=True)
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
        body = self.upload_test_file()
        self.assertTrue(Course.objects.count() == 1)
        self.assertTrue("Duplicate course" in body)

    def upload_test_file(self):
        """Used multiple times in tests"""
        with open(get_course_zip(), "rb") as post_file:
            resp = self.client.post(
                "/importer/upload/{0}".format(self.repo.id),
                {"course_file": post_file, "repository": self.repo.id},
                follow=True
            )
        return resp.content.decode("utf-8")

    def test_invalid_form(self):
        """Upload invalid form"""
        resp = self.client.post(
            "/importer/upload/{0}".format(self.repo.id),
            {}, follow=True
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        log.debug(body)
        self.assertTrue("This field is required." in body)
