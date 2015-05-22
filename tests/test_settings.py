"""
Validate that our settings functions work, and we can create yaml files
"""
import imp
import os
import sys
import tempfile

from django.conf import settings
from django.core import mail
from django.test import TestCase
import mock
import yaml

from lore.settings import load_fallback, get_var


class TestSettings(TestCase):
    """Validate that settings work as expected."""

    def reload_settings(self):
        """
        Reload settings module with cleanup to restore it.

        Returns:
            dict: dictionary of the newly reloaded settings ``vars``
        """
        imp.reload(sys.modules['lore.settings'])
        # Restore settings to original settings after test
        self.addCleanup(imp.reload, sys.modules['lore.settings'])
        return vars(sys.modules['lore.settings'])

    def test_load_fallback(self):
        """Verify our YAML load works as expected."""
        config_settings = {'TEST_KEY': 'yessir'}
        _, temp_config_path = tempfile.mkstemp()
        self.addCleanup(os.remove, temp_config_path)
        with open(temp_config_path, 'w') as temp_config:
            temp_config.write(yaml.dump(config_settings))

        with mock.patch('lore.settings.CONFIG_PATHS') as config_paths:
            config_paths.__iter__.return_value = [temp_config_path]
            fallback_config = load_fallback()
            self.assertDictEqual(fallback_config, config_settings)

    def test_get_var(self):
        """Verify that get_var does the right thing with precedence"""
        with mock.patch.dict(
            'lore.settings.FALLBACK_CONFIG',
            {'FOO': 'bar'}
        ):
            # Verify fallback
            self.assertEqual(get_var('FOO', 'notbar'), 'bar')

        # Verify default value
        self.assertEqual(get_var('NOTATHING', 'foobar'), 'foobar')

        # Verify environment variable wins:
        with mock.patch.dict(
            'os.environ', {'FOO': 'notbar'}, clear=True
        ):
            self.assertEqual(get_var('FOO', 'lemon'), 'notbar')

        # Verify that types work:
        with mock.patch.dict(
            'os.environ',
            {
                'FOO': 'False',
                'BAR': '[1,2,3]',
            },
            clear=True
        ):
            self.assertFalse(get_var('FOO', True))
            self.assertEqual(get_var('BAR', []), [1, 2, 3])
        # Make sure real types still work too (i.e. from yaml load)
        with mock.patch.dict(
            'lore.settings.FALLBACK_CONFIG',
            {'BLAH': True}
        ):
            self.assertEqual(get_var('BLAH', False), True)

    def test_cas_settings(self,):
        """Verify CAS settings get set correctly"""
        with mock.patch.dict('os.environ', {
            'LORE_USE_CAS': 'yep',
            'LORE_CAS_URL': 'foobar'
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertTrue(settings_vars['CAS_ENABLED'])
            self.assertEqual(settings_vars['CAS_SERVER_URL'], 'foobar')

        # Test settings with CAS disabled
        with mock.patch.dict('os.environ', {
            'LORE_USE_CAS': '',
            'LORE_CAS_URL': 'foobar'
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertFalse(settings_vars['CAS_ENABLED'])

    def test_admin_settings(self):
        """Verify that we configure email with environment variable"""

        with mock.patch.dict('os.environ', {
            'LORE_ADMIN_EMAIL': ''
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertFalse(settings_vars.get('ADMINS', False))

        test_admin_email = 'cuddle_bunnies@example.com'
        with mock.patch.dict('os.environ', {
            'LORE_ADMIN_EMAIL': test_admin_email,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertEqual(
                (('Admins', test_admin_email),),
                settings_vars['ADMINS']
            )
        # Manually set ADMIN to our test setting and verify e-mail
        # goes where we expect
        settings.ADMINS = (('Admins', test_admin_email),)
        mail.mail_admins('Test', 'message')
        self.assertIn(test_admin_email, mail.outbox[0].to)
