"""
Testing of project level URLs.
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from urltools import compare


class TestURLs(TestCase):
    """Verify project level URL configuration."""

    def test_cas_enabled(self):
        """Verify that CAS is wired up properly when enabled"""
        with self.settings(
            CAS_ENABLED=True,
            CAS_SERVER_URL='http://example.com/login',
        ):
            # Because this won't actually work, we get in a redirect
            # loop, or at least, best as I can tell.
            response = self.client.get(reverse('cas_login'))
            self.assertTrue(compare(
                'http://example.com/login?'
                'service=http%3A%2F%2Ftestserver%2Fcas%2Flogin%3Fnext%3D%252F',
                response['location']
            ))

    def test_cas_disable(self):
        """Verify that when CAS is disabled, login is default"""
        with self.settings(
            CAS_ENABLED=False
        ):
            response = self.client.get('/login', follow=True)
            self.assertEqual(404, response.status_code)
