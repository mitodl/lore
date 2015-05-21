"""
Testing of project level URLs.
"""

import imp
import sys

from django.conf import settings
from django.test import TestCase
from django.test.client import RedirectCycleError
from django.utils.importlib import import_module
from urltools import compare


def reload_url_conf():
    """Reloads URLs when they are changed by settings"""
    if settings.ROOT_URLCONF in sys.modules:
        imp.reload(sys.modules[settings.ROOT_URLCONF])
    import_module(settings.ROOT_URLCONF)


class TestURLs(TestCase):
    """Verify project level URL configuration."""

    def test_cas_enabled(self):
        """Verify that CAS is wired up properly when enabled"""
        with self.settings(
            CAS_ENABLED=True,
            CAS_SERVER_URL='http://example.com/login',
            CAS_EXTRA_LOGIN_PARAMS={
                'provider': 'touchstone',
                'appname': "LORE"
            }
        ):
            reload_url_conf()
            # Because this won't actually work, we get in a redirect
            # loop, or at least, best as I can tell.
            with self.assertRaises(RedirectCycleError) as context_manager:
                self.client.get('/login/', follow=True)
            exception = context_manager.exception
            self.assertTrue(compare(
                'http://example.com/login/?appname=LORE&'
                'service=http%3A%2F%2Fexample.com%2Flogin%2F%3Fnext%3D%252F'
                '&provider=touchstone',
                exception.last_response['location']
            ))

    def test_cas_disable(self):
        """Verify that when CAS is disabled, login is default"""
        with self.settings(
            CAS_ENABLED=False
        ):
            reload_url_conf()
            response = self.client.get('/login', follow=True)
            self.assertEqual(404, response.status_code)
