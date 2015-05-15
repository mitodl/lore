"""Test application configuration for CAS app"""
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
import mock

from cas.conf import CASAppConf


class CASTestConf(TestCase):
    """Validate that application configuration works as expected."""

    def test_cas_settings_modifications(self,):
        """Verify CAS settings get set correctly"""

        with mock.patch('cas.conf.settings') as patch_settings:
            patch_settings.CAS_ENABLED = True
            patch_settings.CAS_SERVER_URL = 'foobar'
            patch_settings.MIDDLEWARE_CLASSES = ()
            patch_settings.INSTALLED_APPS = ()
            patch_settings.AUTHENTICATION_BACKENDS = ()

            self.assertTrue(CASAppConf().configure_enabled(''))
            settings_vars = vars(patch_settings)
            self.assertTrue(
                set(dict(
                    CAS_ENABLED=True,
                    LOGIN_URL='/login/',
                    LOGIN_REDIRECT_URL='/',
                    CAS_SERVER_URL='foobar'
                )).issubset(set(settings_vars))
            )
            self.assertIn(
                'django_cas_ng.middleware.CASMiddleware',
                settings_vars['MIDDLEWARE_CLASSES']
            )
            self.assertIn(
                'django_cas_ng.backends.CASBackend',
                settings_vars['AUTHENTICATION_BACKENDS']
            )
            self.assertIn('django_cas_ng', settings_vars['INSTALLED_APPS'])

        # Test settings with CAS disabled
        with mock.patch('cas.conf.settings') as patch_settings:
            patch_settings.CAS_ENABLED = False
            self.assertFalse(CASAppConf().configure_enabled(''))
            self.assertFalse(patch_settings.LOGIN_REDIRECT_URL == '/')

    def test_cas_urls(self):
        """Verify we are putting up the correct urls and views"""
        login_url = reverse('cas_login')
        logout_url = reverse('cas_logout')
        self.assertTrue(login_url.endswith('/login'))
        self.assertTrue(logout_url.endswith('/logout'))
        self.assertEqual(
            resolve(login_url).func.__name__, 'login'
        )
        self.assertEqual(
            resolve(logout_url).func.__name__, 'logout'
        )
