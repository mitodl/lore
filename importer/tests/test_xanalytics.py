"""
Tests for hitting the xanalytics Celery tasks.
"""

from __future__ import unicode_literals

import json
import logging

from django.conf import settings
import responses

from importer.tasks import populate_xanalytics_fields, check_for_results
from learningresources.tests.base import LoreTestCase

log = logging.getLogger(__name__)
# pylint: disable=no-self-use


class TestAPI(LoreTestCase):
    """
    Tests using mocks to avoid actual HTTP requests.
    """
    def setUp(self):
        """Override setting."""
        super(TestAPI, self).setUp()
        self.original_url = settings.XANALYTICS_URL
        settings.XANALYTICS_URL = "http://example.com"

    def tearDown(self):
        """Restore original setting."""
        super(TestAPI, self).tearDown()
        settings.XANALYTICS_URL = self.original_url

    @responses.activate
    def test_populate_xanalytics_fields(self):
        """Test kicking off a request."""
        responses.add(
            responses.POST,
            'http://example.com/create',
            body='{"token": "abcde"}',
            content_type="application/json"
        )
        populate_xanalytics_fields(1234)

    @responses.activate
    def test_check_for_results_waiting(self):
        """Test kicking off a request."""
        reply = {"status": "still busy"}
        responses.add(
            responses.POST,
            'http://example.com/status',
            body=json.dumps(reply),
            content_type="application/json"
        )
        check_for_results("abcde", 10, 1)

    @responses.activate
    def test_check_for_results_done(self):
        """Test kicking off a request."""
        file_reply = {
            "course_id": "123",
            "module_medata": [
                {
                    "module_id": "1",
                    "xa_nr_views": "3",
                    "xa_nr_attempts": "25"
                },
                {
                    "module_id": "2",
                    "xa_nr_views": "7",
                    "xa_nr_attempts": "99"

                }
            ]
        }
        responses.add(
            responses.GET,
            'http://example.com/foo.json',
            body=json.dumps(file_reply),
            content_type="application/json"
        )

        reply = {"status": "complete", "url": "http://example.com/foo.json"}
        responses.add(
            responses.POST,
            'http://example.com/status',
            body=json.dumps(reply),
            content_type="application/json"
        )
        check_for_results("abcde", 10, 1)

    @responses.activate
    def test_check_for_results_bad(self):
        """Test kicking off a request."""
        responses.add(
            responses.GET,
            'http://example.com/foo.json',
            body='{"invalid": "JSON", "because": "developer comma",}',
            content_type="application/json"
        )
        reply = {"status": "complete", "url": "http://example.com/foo.json"}
        responses.add(
            responses.POST,
            'http://example.com/status',
            body=json.dumps(reply),
            content_type="application/json"
        )
        self.assertRaises(
            ValueError,
            check_for_results("abcde", 10, 1)
        )
