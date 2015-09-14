"""
Unit tests for REST api
"""
from __future__ import unicode_literals

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)

from learningresources.models import LearningResource
from rest.tests.base import (
    RESTTestCase,
    API_BASE,
    REPO_BASE,
    as_json,
)
from rest.pagination import LorePagination


class TestMisc(RESTTestCase):
    """
    REST test
    """

    def test_root(self):
        """
        Test root of API
        """
        resp = self.client.get(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.post(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.head(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.patch(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.put(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.options(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)

        self.logout()
        resp = self.client.get(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.post(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.head(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.patch(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.put(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.options(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)

    def test_pagination(self):
        """
        Test page_size query parameter.
        """
        self.import_course_tarball(self.repo)

        num_resources = LearningResource.objects.filter(
            course__repository__id=self.repo.id
        ).count()

        def assert_page_size(page_size):
            """
            Helper function to assert len(results) == page_size.
            """
            if page_size is None:
                page_size_param = ""
                page_size = LorePagination.page_size
            else:
                page_size_param = "?page_size={page_size}".format(
                    page_size=page_size
                )
            resp = self.client.get(
                "{repo_base}{repo_slug}/"
                "learning_resources/{page_size_param}".format(
                    repo_base=REPO_BASE,
                    repo_slug=self.repo.slug,
                    page_size_param=page_size_param
                )
            )
            self.assertEqual(resp.status_code, HTTP_200_OK)
            resources = as_json(resp)
            self.assertTrue(len(resources['results']) <= page_size)
            self.assertEqual(resources['count'], num_resources)

        assert_page_size(2)
        assert_page_size(10)
        assert_page_size(None)
