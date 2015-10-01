"""
Adds coverage for search app managemnet commands.
"""

from __future__ import unicode_literals

from django.core.management import call_command
from mock import patch

from learningresources.tests.base import LoreTestCase
from search import utils


class TestManagementCommands(LoreTestCase):
    """
    Call management commands for test coverage.
    """

    # pylint: disable=invalid-name, no-self-use
    def test_refresh_index(self):
        """
        Test refresh_index call.
        """
        with patch.object(utils, 'index_resources') as mock_method:
            mock_method.return_value = None
            self.assertEqual(mock_method.call_count, 0)
            call_command('refresh_index')
            self.assertEqual(mock_method.call_count, 1)

    def test_recreate_index(self):
        """
        Test recreate_index call.
        """
        with patch.object(utils, 'clear_index') as mock_method:
            mock_method.return_value = None
            self.assertEqual(mock_method.call_count, 0)
            call_command('recreate_index')
            self.assertEqual(mock_method.call_count, 1)
