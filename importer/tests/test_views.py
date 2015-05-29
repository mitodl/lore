"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging

from learningresources.models import LearningResource, Course
from learningresources.tests.base import LoreTestCase

from .test_import import get_course_zip

HTTP_OK = 200

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
        resp = self.client.get("/importer/upload", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('enctype="multipart/form-data"' in body)

    def test_upload_post(self):
        """POST upload page."""
        self.assertTrue(LearningResource.objects.count() == 0)
        body = self.upload_test_file()
        self.assertTrue(LearningResource.objects.count() == 5)
        # We should have been redirected to the Listing page.
        self.assertTrue('<h1>Listing</h1>' in body)

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
                "/importer/upload/",
                {"course_file": post_file, "repository": self.repo.id},
                follow=True
            )
        return resp.content.decode("utf-8")
