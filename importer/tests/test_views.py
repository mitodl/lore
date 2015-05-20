"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

from django.test import Client
from django.test.testcases import TestCase

HTTP_OK = 200


class TestViews(TestCase):
    """Hit each view."""

    def test_status_get(self):
        """Status page."""
        client = Client()
        resp = client.get("/importer/status", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("Number of learning objects:" in body)

    def test_upload_get(self):
        """Status page."""
        client = Client()
        resp = client.get("/importer/upload", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('enctype="multipart/form-data"' in body)
