"""
Tests for the status module.
"""
from __future__ import unicode_literals

from copy import deepcopy
import json
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client
from django.test.testcases import TestCase

log = logging.getLogger(__name__)

HTTP_OK = 200
SERVICE_UNAVAILABLE = 503


class TestStatus(TestCase):
    """Test output of status page."""

    def setUp(self):
        """
        Set up client and remember settings for PostgreSQL, Redis,
        and Elasticsearch. Changes made to django.conf.settings during
        tests persist beyond the test scope, so if they are changed
        we need to restore them.
        """

        # Create test client.
        self.client = Client()
        self.url = reverse("status")
        super(TestStatus, self).setUp()

    def get(self, expected_status=HTTP_OK):
        """Get the page."""
        resp = self.client.get(self.url, data={"token": settings.STATUS_TOKEN})
        self.assertEqual(resp.status_code, expected_status)
        return json.loads(resp.content.decode('utf-8'))

    def test_view(self):
        """Get normally."""
        resp = self.get()
        for key in ("postgresql", "redis", "elasticsearch"):
            self.assertTrue(resp[key]["status"] == "up")

    def test_no_settings(self):
        """Missing settings."""
        (broker_url, databases, haystack_connections) = (
            settings.BROKER_URL,
            settings.DATABASES,
            settings.HAYSTACK_CONNECTIONS
        )
        try:
            del settings.BROKER_URL
            del settings.DATABASES
            del settings.HAYSTACK_CONNECTIONS
            resp = self.get()
            for key in ("postgresql", "redis", "elasticsearch"):
                self.assertTrue(resp[key]["status"] == "no config found")
        finally:
            (
                settings.BROKER_URL,
                settings.DATABASES,
                settings.HAYSTACK_CONNECTIONS,
            ) = (broker_url, databases, haystack_connections)

    def test_broken_settings(self):
        """Settings that couldn't possibly work."""
        junk = " not a chance "
        broker_url = junk
        databases = deepcopy(settings.DATABASES)
        databases['default'] = junk
        haystack_connections = deepcopy(settings.HAYSTACK_CONNECTIONS)
        haystack_connections["default"]["URL"] = junk
        with self.settings(
            BROKER_URL=broker_url,
            DATABASES=databases,
            HAYSTACK_CONNECTIONS=haystack_connections
        ):
            resp = self.get(SERVICE_UNAVAILABLE)
            for key in ("postgresql", "redis", "elasticsearch"):
                self.assertTrue(resp[key]["status"] == "down")

    def test_invalid_settings(self):
        """
        Settings that look right, but aren't (if service is actually down).
        """
        broker_url = "redis://bogus:6379/4"
        databases = deepcopy(settings.DATABASES)
        databases["default"]["HOST"] = "monkey"
        haystack_connections = deepcopy(settings.HAYSTACK_CONNECTIONS)
        haystack_connections["default"]["URL"] = "pizza:2300"
        with self.settings(
            BROKER_URL=broker_url,
            DATABASES=databases,
            HAYSTACK_CONNECTIONS=haystack_connections
        ):
            resp = self.get(SERVICE_UNAVAILABLE)
            for key in ("postgresql", "redis", "elasticsearch"):
                self.assertTrue(resp[key]["status"] == "down")

    def test_token(self):
        """
        Caller must have correct token, or no dice. Having a good token
        is tested in all the other tests.
        """

        # No token.
        resp = self.client.get(self.url)
        self.assertTrue(resp.status_code == 404)

        # Invalid token.
        resp = self.client.get(self.url, {"token": "gibberish"})
        self.assertTrue(resp.status_code == 404)
