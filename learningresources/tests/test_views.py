"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

from learningresources.models import Repository

from .base import LoreTestCase

HTTP_OK = 200


class TestViews(LoreTestCase):
    """Hit each view."""

    def test_welcome(self):
        """Welcome page."""
        resp = self.client.get("/lore/welcome", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("<h1>Welcome</h1>" in body)

    def test_create_repo_get(self):
        """GET repo creation page."""
        resp = self.client.get("/lore/create_repo", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('<h1>Create repository</h1>' in body)

    def test_upload_post(self):
        """POST upload page."""
        self.assertTrue(Repository.objects.count() == 0)
        self.client.post(
            "/lore/create_repo/",
            {"name": "test name", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.count() == 1)
