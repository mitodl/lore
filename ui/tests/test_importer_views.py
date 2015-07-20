"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

import logging

from django.core.files.storage import default_storage
import mock

from learningresources.models import LearningResource, Course
from learningresources.tests.base import LoreTestCase
from roles.api import assign_user_to_repo_group, remove_user_from_repo_group
from roles.api import GroupTypes
from ui.views import RepositoryView

HTTP_OK = 200
UNAUTHORIZED = 403
NOT_FOUND = 404

log = logging.getLogger(__name__)


class TestViews(LoreTestCase):
    """Hit each view."""

    def setUp(self):
        super(TestViews, self).setUp()
        self.import_url = "/repositories/{0}/import/"
        self.import_url_slug = self.import_url.format(self.repo.slug)
        self.repository_url = "/repositories/{0}/"
        self.repository_url_slug = self.repository_url.format(self.repo.slug)

    def test_upload_get(self):
        """GET upload page."""
        resp = self.client.get(self.import_url_slug, follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('enctype="multipart/form-data"' in body)

    def test_upload_get_bad_repo(self):
        """GET upload page."""
        self.assert_status_code(self.import_url.format("999"), NOT_FOUND)

    def test_upload_with_permissions(self):
        """GET upload page with different user permissions"""
        def check_user_no_permission():
            """
            Helper function to check that the user has
            no permission on the repo
            """
            # user cannot see the repository page
            self.assert_status_code(
                self.repository_url_slug,
                UNAUTHORIZED
            )
            # and cannot see the import page
            self.assert_status_code(
                self.import_url_slug,
                UNAUTHORIZED
            )
        self.logout()
        self.login(self.USERNAME_NO_REPO)
        # user has no permissions at all
        check_user_no_permission()
        # user has author permissions
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        # user can see the repository page
        self.assert_status_code(
            self.repository_url_slug,
            HTTP_OK
        )
        # but cannot see the import for the repo
        self.assert_status_code(
            self.import_url_slug,
            UNAUTHORIZED
        )
        # user has no permissions
        remove_user_from_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        check_user_no_permission()
        # user has curator permissions
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        # user can see the repository page
        self.assert_status_code(
            self.repository_url_slug,
            HTTP_OK
        )
        # and can see the the import for the repo
        self.assert_status_code(
            self.import_url_slug,
            HTTP_OK
        )
        # remove curator permissions
        remove_user_from_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        check_user_no_permission()
        # user has admin permissions
        assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        # user can see the repository page
        self.assert_status_code(
            self.repository_url_slug,
            HTTP_OK
        )
        # and can see the the import for the repo
        self.assert_status_code(
            self.import_url_slug,
            HTTP_OK
        )

    def test_upload_post(self):
        """POST upload page."""
        original_count = LearningResource.objects.count()
        resp = self.upload_test_file()
        self.assertEqual(
            LearningResource.objects.count(),
            original_count + self.toy_resource_count,
        )
        # We should have been redirected to the Listing page.
        self.assertContains(resp, 'Listing</title>')

    def test_upload_duplicate(self):
        """Gracefully inform the user."""
        original_count = Course.objects.count()
        self.upload_test_file()
        self.assertTrue(Course.objects.count() == original_count + 1)
        self.upload_test_file()
        self.assertTrue(Course.objects.count() == original_count + 1)

    def upload_test_file(self):
        """Used multiple times in tests"""
        with default_storage.open(self.get_course_zip(), "rb") as post_file:
            resp = self.client.post(
                self.import_url_slug,
                {"course_file": post_file, "repository": self.repo.id},
                follow=True
            )
        return resp

    def test_invalid_form(self):
        """Upload invalid form"""
        resp = self.client.post(
            self.import_url_slug,
            {}, follow=True
        )
        self.assertContains(resp, "This field is required.")

    def test_wiped_index(self):
        """
        If the Elasticsearch index is erased, it caused a KeyError
        when accessing the repository page until Django is restarted.
        """
        repo_view = RepositoryView()
        repo_view.repo = self.repo
        repo_view.request = mock.MagicMock()
        with mock.patch('ui.views.get_perms') as _:
            with mock.patch(
                'ui.views.FacetedSearchView.extra_context'
            ) as mocked_context:
                no_fields = {'facets': {}}
                with_fields = {'facets': {'fields': {'item': 'foo'}}}
                mocked_context.return_value = no_fields
                context = repo_view.extra_context()
                self.assertEqual(no_fields, context)
                mocked_context.return_value = with_fields
                context = repo_view.extra_context()
                self.assertEqual(context['repo'], self.repo)
