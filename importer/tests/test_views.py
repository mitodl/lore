"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

from learningresources.models import LearningResource
from learningresources.tests.test_case import LoreTestCase

from .test_import import get_course_zip

HTTP_OK = 200


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
        with open(get_course_zip(), "rb") as post_file:
            self.client.post(
                "/importer/upload/",
                {"course_file": post_file},
                follow=True
            )
        self.assertTrue(LearningResource.objects.count() == 5)
