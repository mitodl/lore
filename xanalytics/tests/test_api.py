"""
Tests for hitting the xanalytics API.
"""

import json
import logging
from unittest import TestCase

from django.conf import settings
import responses
from six import BytesIO

from xanalytics import send_request, get_result, _call

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


class TestBadData(TestCase):
    """
    Assume the worst from the xanalytics API.
    """
    def setUp(self):
        """Override setting."""
        super(TestBadData, self).setUp()
        self.original_url = settings.XANALYTICS_URL
        settings.XANALYTICS_URL = "http://example.com"

    def tearDown(self):
        """Restore original setting."""
        super(TestBadData, self).tearDown()
        settings.XANALYTICS_URL = self.original_url

    @responses.activate
    def test_server_down(self):
        """Endpoint unavailable."""
        resp = _call(settings.XANALYTICS_URL, {})
        self.assertEqual(resp, {})

    @responses.activate
    def test_binary(self):
        """
        Binary data received. This also implicitly tests malformed
        JSON, and any content received along with a non-200 error.
        """
        responses.add(
            responses.POST,
            settings.XANALYTICS_URL,
            body=BytesIO("hello").getvalue(),
            content_type="application/octet-stream",
        )
        resp = _call(settings.XANALYTICS_URL, {})
        self.assertEqual(resp, {})
