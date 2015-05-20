"""
Validate that our settings functions work, and we can create yaml files
"""
import os
import tempfile
import unittest

import mock
import yaml

from lore.settings import load_fallback, get_var


class TestSettings(unittest.TestCase):
    """Validate that settings work as expected."""

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

    @mock.patch.dict('lore.settings.FALLBACK_CONFIG', {'FOO': 'bar'})
    def test_get_var(self):
        """Verify that get_var does the right thing with precedence"""
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
