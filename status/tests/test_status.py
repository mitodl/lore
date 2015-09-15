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

        # Remember settings in case they're mutilated during a test.
        self.original_settings = (
            settings.BROKER_URL,
            deepcopy(settings.DATABASES),
            deepcopy(settings.HAYSTACK_CONNECTIONS),
        )

    def tearDown(self):
        """Restore settings after each test."""
        (
            settings.BROKER_URL,
            settings.DATABASES,
            settings.HAYSTACK_CONNECTIONS,
        ) = self.original_settings
        super(TestStatus, self).tearDown()

    def get(self, expected_status=HTTP_OK):
        """Get the page."""
        resp = self.client.get(self.url, data={"token": settings.STATUS_TOKEN})
        self.assertEqual(resp.status_code, expected_status)
        jsn = json.loads(resp.content.decode('utf-8'))
        log.info(jsn)
        return jsn

    def test_view(self):
        """Get normally."""
        resp = self.get()
        for key in ("postgresql", "redis", "elasticsearch"):
            self.assertTrue(resp[key]["status"] == "up")

    def test_no_settings(self):
        """Missing settings."""
        del settings.BROKER_URL
        del settings.DATABASES
        del settings.HAYSTACK_CONNECTIONS
        resp = self.get()
        for key in ("postgresql", "redis", "elasticsearch"):
            self.assertTrue(resp[key]["status"] == "no config found")

    def test_broken_settings(self):
        """Settings that couldn't possibly work."""
        junk = " not a chance "
        settings.BROKER_URL = junk
        settings.DATABASES["default"] = junk
        settings.HAYSTACK_CONNECTIONS["default"]["URL"] = junk
        resp = self.get(SERVICE_UNAVAILABLE)
        for key in ("postgresql", "redis", "elasticsearch"):
            self.assertTrue(resp[key]["status"] == "down")

    def test_invalid_settings(self):
        """
        Settings that look right, but aren't (if service is actually down).
        """
        settings.BROKER_URL = "redis://bogus:6379/4"
        settings.DATABASES["default"]["HOST"] = "monkey"
        settings.HAYSTACK_CONNECTIONS["default"]["URL"] = "pizza:2300"
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
