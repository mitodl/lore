"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging

from django.core.urlresolvers import reverse

from learningresources.models import Repository
from roles.api import assign_user_to_repo_group, remove_user_from_repo_group
from roles.permissions import GroupTypes

from .base import LoreTestCase

HTTP_OK = 200
UNAUTHORIZED = 403
NOT_FOUND = 404

log = logging.getLogger(__name__)


class TestViews(LoreTestCase):
    """Hit each view."""

    def setUp(self):
        super(TestViews, self).setUp()
        self.repository_url = "/repositories/{0}/".format(self.repo.slug)

    def test_get_home(self):
        """Home Page."""
        body = self.assert_status_code("/home", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)

        body = self.assert_status_code("/", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)
        self.assertTrue('>Create repository</a>' in body)

    def test_get_home_norepo(self):
        """Home Page with no authorization to create repositories"""
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        body = self.assert_status_code("/home", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)

        body = self.assert_status_code("/", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)
        self.assertFalse('<a href="/lore/create_repo/">'
                         'Create repository</a>' in body)

    def test_create_repo_post(self):
        """Create repo."""
        repo_name = "my really sweet repository"
        resp = self.client.post(
            "/repositories/new/",
            {"name": repo_name, "description": "foo"},
            follow=True,
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue(repo_name in body)

    def test_listing_unauthorized(self):
        """View listing page."""
        # Not authorized to view this repository...
        body = self.assert_status_code(
            "/repositories/99/",
            UNAUTHORIZED,
            return_body=True
        )
        self.assertTrue("unauthorized" in body)

    def test_listing_importcourse_perms(self):
        """
        Tests the listing page with different user permissions
        to check who can see the import course html
        """
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        # user has no permissions at all
        self.assert_status_code(
            self.repository_url,
            UNAUTHORIZED
        )
        # user has author permissions and cannot see the import for the repo
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        body = self.assert_status_code(
            self.repository_url,
            HTTP_OK,
            return_body=True
        )
        self.assertFalse("Import Course</a>" in body)
        # user has no permissions
        remove_user_from_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        self.assert_status_code(
            self.repository_url,
            UNAUTHORIZED
        )
        # user has curator permissions and can see the the import for the repo
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        body = self.assert_status_code(
            self.repository_url,
            HTTP_OK,
            return_body=True
        )
        self.assertTrue("Import Course</a>" in body)
        # user has no permissions
        remove_user_from_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        self.assert_status_code(
            self.repository_url,
            UNAUTHORIZED
        )
        # user has admin permissions and can see the the import for the repo
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        body = self.assert_status_code(
            self.repository_url,
            HTTP_OK,
            return_body=True
        )
        self.assertTrue("Import Course</a>" in body)

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
            "/repositories/new/",
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
            "/repositories/new/",
            {"name": "awesome repo", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.filter(slug=slug).exists())
        self.client.post(
            "/repositories/new/",
            {"name": "awesome       repo", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.filter(slug=slug1).exists())

    def test_invalid_repo_form(self):
        """Upload invalid form"""
        resp = self.client.post(
            "/repositories/new/",
            {}, follow=True
        )
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("This field is required." in body)
        self.assertTrue(Repository.objects.count() == 1)

    def test_export_good(self):
        """Get raw XML of something I should be allowed to see."""
        url = reverse("export", args=(self.resource.id,))
        resp = self.client.get(url, follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue(resp.status_code == HTTP_OK)
        self.assertTrue(self.resource.content_xml in body)

    def test_export_no_permission(self):
        """Get raw XML of something I should not be allowed to see."""
        url = reverse("export", args=(self.resource.id,))
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        resp = self.client.get(url, follow=True)
        self.assertTrue(resp.status_code == UNAUTHORIZED)

    def test_export_nonexistent(self):
        """Get raw XML of something than does not exist."""
        url = reverse("export", args=(999999,))
        resp = self.client.get(url, follow=True)
        self.assertTrue(resp.status_code == NOT_FOUND)
