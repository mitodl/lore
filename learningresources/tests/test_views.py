"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

from learningresources.models import Repository

from .base import LoreTestCase

HTTP_OK = 200
UNAUTHORIZED = 403


class TestViews(LoreTestCase):
    """Hit each view."""

    def test_get_home(self):
        """Welcome page."""
        resp = self.client.get("/home", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("Welcome" in body)

        resp = self.client.get("/", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("Welcome" in body)

    def test_create_repo_post(self):
        """Create repo."""
        repo_name = "my really sweet repository"
        resp = self.client.post(
            "/repositories/new",
            {"name": repo_name, "description": "foo"},
            follow=True,
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue(repo_name in body)
        # Should have been redirected to the welcome page.
        self.assertTrue("Viewing Repository: {0}".format(repo_name) in body)

    def test_listing_unauthorized(self):
        """View listing page."""
        # Not authorized to view this repository...
        resp = self.client.get("/repositories/99/1", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue(resp.status_code == UNAUTHORIZED)
        self.assertTrue("unauthorized" in body)

    def test_welcome(self):
        """Welcome page."""
        resp = self.client.get("/home", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("<h1>Welcome</h1>" in body)

    def test_create_repo_get(self):
        """GET repo creation page."""
        resp = self.client.get("/repositories/new", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('<h1>Create repository</h1>' in body)

    def test_upload_post(self):
        """POST upload page."""
        # We have the default self.repo in the database...
        self.assertTrue(Repository.objects.count() == 1)
        self.client.post(
            "/repositories/new",
            {"name": "test name", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.count() == 2)

    def test_upload_dupe_slug(self):
        """slug must be unique"""
        # We have the default self.repo in the database...
        slug = "awesome-repo"
        slug1 = "awesome-repo1"
        self.assertFalse(Repository.objects.filter(slug=slug).exists())
        self.assertFalse(Repository.objects.filter(slug=slug1).exists())
        self.client.post(
            "/repositories/new",
            {"name": "awesome repo", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.filter(slug=slug).exists())
        self.client.post(
            "/repositories/new",
            {"name": "awesome       repo", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.filter(slug=slug1).exists())

    def test_invalid_repo_form(self):
        """Upload invalid form"""
        resp = self.client.post(
            "/repositories/new",
            {}, follow=True
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("This field is required." in body)
