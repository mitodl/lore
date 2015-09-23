"""
Tests for repository views.
"""

from __future__ import unicode_literals

import json

from rest_framework.status import HTTP_201_CREATED

from learningresources.tests.base import LoreTestCase
from rest.pagination import LorePagination
from search.sorting import LoreSortingFields


class TestRepositoryViews(LoreTestCase):
    """
    Tests for repository views.
    """

    def assert_page_size(self, page_size, expected_page_size):
        """
        Helper function to assert page size in context.
        """
        if page_size is not None:
            page_size_param = "?{query_param}={page_size}".format(
                query_param=LorePagination.page_size_query_param,
                page_size=page_size
            )
        else:
            page_size_param = ""

        resp = self.client.get(
            "/repositories/{slug}/{page_size_param}".format(
                slug=self.repo.slug,
                page_size_param=page_size_param
            )
        )
        self.assertEqual(
            json.loads(resp.context['page_size_json']),
            expected_page_size
        )

    def test_page_size(self):
        """
        Test that page size context is set properly.
        """
        self.assert_page_size(2, 2)
        self.assert_page_size(10, 10)
        self.assert_page_size(0, LorePagination.page_size)
        self.assert_page_size(None, LorePagination.page_size)
        self.assert_page_size("xyz", LorePagination.page_size)
        self.assert_page_size(-1, LorePagination.page_size)
        self.assert_page_size(
            LorePagination.max_page_size + 1,
            LorePagination.max_page_size
        )
        self.assert_page_size(
            LorePagination.max_page_size,
            LorePagination.max_page_size
        )
        self.assert_page_size(
            LorePagination.max_page_size - 1,
            LorePagination.max_page_size - 1
        )

    def test_repo(self):
        """
        Test that repo is present.
        """
        resp = self.client.get(
            "/repositories/{slug}/".format(slug=self.repo.slug))
        self.assertEqual(self.repo, resp.context['repo'])

    def test_perms_on_cur_repo(self):
        """
        Test that perms_on_cur_repo context is set.
        """
        resp = self.client.get(
            "/repositories/{slug}/".format(slug=self.repo.slug))
        expected_perms = [
            'manage_repo_users',
            'add_edit_metadata',
            'manage_taxonomy',
            'view_repo',
            'import_course'
        ]
        self.assertEqual(
            sorted(resp.context["perms_on_cur_repo"]),
            sorted(expected_perms)
        )

    def test_exports(self):
        """
        Test presence of exports.
        """
        resp = self.client.get(
            "/repositories/{slug}/".format(slug=self.repo.slug))
        self.assertEqual(json.loads(resp.context["exports_json"]), [])

        lid = self.repo.course_set.first().resources.first().id
        resp = self.client.post(
            "/api/v1/repositories/{slug}/"
            "learning_resource_exports/{user}/".format(
                slug=self.repo.slug,
                user=self.user.username,
            ), {"id": lid})
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        resp = self.client.get(
            "/repositories/{slug}/".format(slug=self.repo.slug))
        self.assertEqual(json.loads(resp.context["exports_json"]), [lid])

    def test_sorting_options(self):
        """
        Test presence of sorting options.
        """

        sortby = "nr_views"
        resp = self.client.get(
            "/repositories/{slug}/?sortby={sortby}".format(
                slug=self.repo.slug,
                sortby=sortby
            )
        )
        self.assertEqual(
            json.loads(resp.context["sorting_options_json"]),
            {
                "current": list(LoreSortingFields.get_sorting_option(sortby)),
                "all": [list(x) for x in
                        LoreSortingFields.all_sorting_options_but(sortby)]
            }
        )
