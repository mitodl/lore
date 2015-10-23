"""
Unit tests for REST api
"""
from __future__ import unicode_literals

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)

from learningresources.models import LearningResourceType
from rest.tests.base import (
    RESTTestCase,
    API_BASE,
    as_json,
)
from rest.pagination import LorePagination
from rest.util import default_slugify


class TestMisc(RESTTestCase):
    """
    REST test
    """

    def assert_page_size(self, page_size, expected_num_results):
        """
        Helper function to assert len(results) == expected_num_results.
        """
        num_types = LearningResourceType.objects.filter().count()

        if page_size is None:
            page_size_param = ""
        else:
            page_size_param = "?{query_param}={page_size}".format(
                query_param=LorePagination.page_size_query_param,
                page_size=page_size
            )
        resp = self.client.get(
            "{api_base}learning_resource_types/{page_size_param}".format(
                api_base=API_BASE,
                page_size_param=page_size_param
            )
        )
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resources = as_json(resp)
        self.assertEqual(len(resources['results']), expected_num_results)
        self.assertEqual(resources['count'], num_types)

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
        types = [
            LearningResourceType(name="type_{i}".format(i=i))
            for i in range(LorePagination.max_page_size + 10)
        ]
        LearningResourceType.objects.bulk_create(types)

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

    def test_default_slugify(self):
        """
        Test for the default slugify function.
        Since this function is generic, here we test the generic call
        """
        # a normal string
        self.assertEqual(
            default_slugify(
                'foo',
                'bar',
                lambda x: False
            ),
            'foo'
        )
        # the normal string already exists
        self.assertEqual(
            default_slugify(
                'foo',
                'bar',
                lambda x: x == 'foo'
            ),
            'foo1'
        )
        # a string that gives an empty slug
        self.assertEqual(
            default_slugify(
                '%^%$',
                'bar',
                lambda x: False
            ),
            'bar-slug'
        )
        # the default slug already exists
        self.assertEqual(
            default_slugify(
                '%^%$',
                'bar',
                lambda x: x == 'bar-slug'
            ),
            'bar-slug1'
        )
