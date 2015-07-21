"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse

import ui.urls
from learningresources.models import Repository, StaticAsset
from roles.api import assign_user_to_repo_group, remove_user_from_repo_group
from roles.permissions import GroupTypes
from search.sorting import LoreSortingFields
from six.moves import reload_module  # pylint: disable=import-error

from learningresources.tests.base import LoreTestCase

HTTP_OK = 200
UNAUTHORIZED = 403
NOT_FOUND = 404

log = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class TestViews(LoreTestCase):
    """Hit each view."""

    def setUp(self):
        super(TestViews, self).setUp()
        self.repository_url = "/repositories/{0}/".format(self.repo.slug)
        self.import_url_slug = "/repositories/{0}/import/".format(
            self.repo.slug
        )

    def upload_test_file(self):
        """Used multiple times in tests"""
        with default_storage.open(self.get_course_zip(), "rb") as post_file:
            resp = self.client.post(
                self.import_url_slug,
                {"course_file": post_file, "repository": self.repo.id},
                follow=True
            )
        return resp.content.decode("utf-8")

    def test_get_home(self):
        """Home Page."""
        body = self.assert_status_code("/home", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)

        body = self.assert_status_code("/", HTTP_OK, return_body=True)
        self.assertTrue("<title>MIT - LORE </title>" in body)
        self.assertTrue('>Create repository</a>' in body)
        self.assertFalse('Request permission to create '
                         'repositories</a>' in body)

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
        self.assertTrue('Request permission to create '
                        'repositories</a>' in body)

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

    def test_listing_not_found(self):
        """View listing page, but repo does not exist."""
        self.assert_status_code(
            "/repositories/99/",
            NOT_FOUND,
            return_body=True
        )

    def test_listing_unauthorized(self):
        """View listing page, but not authorized to view this repository."""
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        self.assert_status_code(
            self.repository_url,
            UNAUTHORIZED,
            return_body=True
        )

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

    def test_repo_post(self):
        """POST repo page."""
        # We have the default self.repo in the database...
        self.assertTrue(Repository.objects.count() == 1)
        self.client.post(
            "/repositories/new/",
            {"name": "test name", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.count() == 2)

    def test_repo_dupe_slug(self):
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

    def test_access_without_login(self):
        """
        Tests the repository page without login
        """
        self.logout()
        response = self.client.get(self.repository_url, follow=True)
        self.assertEqual(response.status_code, 200)
        # we were redirected to login
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertTrue(302 in response.redirect_chain[0])

    def test_export_good(self):
        """Get raw XML of something I should be allowed to see."""
        url = reverse("export", args=(self.repo.slug, self.resource.id))
        resp = self.client.get(url, follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue(resp.status_code == HTTP_OK)
        self.assertTrue(self.resource.content_xml in body)

    def test_export_no_permission(self):
        """Get raw XML of something I should not be allowed to see."""
        url = reverse("export", args=(self.repo.slug, self.resource.id))
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        resp = self.client.get(url, follow=True)
        self.assertTrue(resp.status_code == UNAUTHORIZED)

    def test_export_nonexistent(self):
        """Get raw XML of something than does not exist."""
        url = reverse("export", args=(self.repo.slug, 999999))
        resp = self.client.get(url, follow=True)
        self.assertTrue(resp.status_code == NOT_FOUND)

    def test_repo_url(self):
        """Hit repo site normally."""
        resp = self.client.get(self.repository_url, follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)

    def test_repo_page_num(self):
        """Hit repo site normally."""
        resp = self.client.get(self.repository_url + "?page=1", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)

    def test_repo_course_filter(self):
        """Hit repo site normally."""
        querystring = "?selected_facets=course_exact:{0}".format(
            self.course.course_number)
        resp = self.client.get(self.repository_url + querystring, follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)

    def test_listing_with_sorting(self):
        """
        Hit the listing with sorting and test that the current sorting
        changes in the interface.
        The actual sorting of results is tested in search.tests.test_indexing
        """
        url = self.repository_url + "?sortby={0}"
        base_sorting_str = ('<button type="button" '
                            'class="btn btn-default">{0}</button>')
        # test no sort type
        body = self.assert_status_code(
            self.repository_url,
            HTTP_OK,
            return_body=True
        )
        self.assertIn(
            base_sorting_str.format(
                LoreSortingFields.get_sorting_option(
                    LoreSortingFields.DEFAULT_SORTING_FIELD
                )[1]
            ),
            body
        )
        # test all the allowed sort types
        for sort_option in LoreSortingFields.all_sorting_options():
            sort_url = url.format(sort_option[0])
            body = self.assert_status_code(
                sort_url,
                HTTP_OK,
                return_body=True
            )
            self.assertIn(
                base_sorting_str.format(sort_option[1]),
                body
            )
        # test sorting by not allowed sort type
        url_not_allowed_sort_type = url.format('foo_field')
        body = self.assert_status_code(
            url_not_allowed_sort_type,
            HTTP_OK,
            return_body=True
        )
        self.assertIn(
            base_sorting_str.format(
                LoreSortingFields.get_sorting_option(
                    LoreSortingFields.DEFAULT_SORTING_FIELD
                )[1]
            ),
            body
        )

    def test_description_path(self):
        """Tests that the description path is in the listing page"""
        dpath_html = '<span class="meta-item">{0}</span>'.format(
            self.resource.description_path
        )
        body = self.assert_status_code(
            self.repository_url,
            HTTP_OK,
            return_body=True
        )
        self.assertIn(dpath_html, body)

    def test_serve_media(self):
        """Hit serve media"""
        self.assertEqual(
            settings.DEFAULT_FILE_STORAGE,
            'django.core.files.storage.FileSystemStorage'
        )
        # upload a course
        self.upload_test_file()
        self.assertEqual(len(StaticAsset.objects.all()), 5)
        # take the url of a static asset
        static_asset_url = StaticAsset.objects.all()[0].asset.url
        # hit the view
        resp = self.client.get(static_asset_url)
        self.assertEqual(resp.status_code, HTTP_OK)
        self.assertEqual(
            resp.get('Content-Disposition'),
            'attachment; filename={}'.format(
                os.path.basename(static_asset_url)
            )
        )
        # only the user with right to see the repo can access the file
        self.logout()
        self.login(self.user_norepo.username)
        resp = self.client.get(static_asset_url)
        self.assertEqual(resp.status_code, UNAUTHORIZED)
        # login back with the original user
        self.logout()
        self.login(self.user.username)
        # hit the view with a nonexistent file
        resp = self.client.get('/media/fsdfs2837hwdudnks/foo.txt')
        self.assertEqual(resp.status_code, NOT_FOUND)
        # change the default file storage to S3
        with self.settings(
            DEFAULT_FILE_STORAGE=('storages.backends'
                                  '.s3boto.S3BotoStorage')
        ):
            reload_module(ui.urls)
            # the view is not available any more
            resp = self.client.get(static_asset_url)
            self.assertEqual(resp.status_code, NOT_FOUND)
        # force the reload of the urls again to be sure to have everything back
        reload_module(ui.urls)

    def test_preview_url(self):
        """Test that preview url shows up correctly"""
        resp = self.client.get(self.repository_url, follow=True)
        self.assertIn(
            '<a href="https://www.sandbox.edx.org/courses/test-org/'
            'infinity/Febtober/jump_to_id/url_name1" '
            'target="_blank">Preview</a>',
            resp.content.decode('utf-8'))
