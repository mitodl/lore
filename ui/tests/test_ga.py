"""
Tests for repository views
"""
from __future__ import unicode_literals

from django.test.utils import override_settings

from learningresources.tests.base import LoreTestCase


class TestGoogleAnalytics(LoreTestCase):
    """Test the Google Analytics setting."""

    @override_settings(GOOGLE_ANALYTICS_ID='')
    def test_analytics_blank(self):
        """Verify with the analytics set and not set."""
        self.login(self.USERNAME)
        response = self.client.get('/')
        self.assertNotContains(response, "ga('send', 'pageview');")

    @override_settings(GOOGLE_ANALYTICS_ID=None)
    def test_analytics_none(self):
        """Verify with the analytics set and not set."""
        self.login(self.USERNAME)
        response = self.client.get('/')
        self.assertNotContains(response, "ga('send', 'pageview');")

    @override_settings(GOOGLE_ANALYTICS_ID='totally-unique-ga-id')
    def test_analytics_with_id(self):
        """Verify with the analytics set and not set."""
        self.login(self.USERNAME)
        response = self.client.get('/')
        self.assertContains(response, "ga('send', 'pageview');")
        self.assertContains(response, "totally-unique-ga-id")
