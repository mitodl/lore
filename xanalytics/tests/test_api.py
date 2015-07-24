"""
Tests for hitting the xanalytics API.
"""

import json
import logging
from unittest import TestCase

from django.conf import settings
import responses

from xanalytics import send_request, get_result

log = logging.getLogger(__name__)


class TestAPI(TestCase):
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
    def test_send_request(self):
        """Test kicking off a request."""
        responses.add(
            responses.POST,
            'http://example.com/create',
            body='{"token": "abcde"}',
            content_type="application/json"
        )
        resp = send_request(settings.XANALYTICS_URL + "/create", 1234)
        self.assertEqual(resp["token"], "abcde")

    @responses.activate
    def test_get_result(self):
        """Check status of request."""
        reply = {"status": "success", "url": "http://example.com/foo.json"}
        responses.add(
            responses.POST,
            'http://example.com/status',
            body=json.dumps(reply),
            content_type="application/json"
        )
        self.assertEqual(get_result(
            settings.XANALYTICS_URL + "/status", 1234)["status"], "success")
