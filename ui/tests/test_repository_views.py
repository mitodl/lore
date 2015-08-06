"""
Tests for repository views
"""

from __future__ import unicode_literals

import json

from rest_framework.status import HTTP_200_OK

from learningresources.tests.base import LoreTestCase
from learningresources.models import LearningResource


class TestViews(LoreTestCase):
    """Test repository view."""

    def test_export_button(self):
        """Make sure export button is visible at the appropriate times."""
        repo_url = '/repositories/{repo}/'.format(repo=self.repo.slug)
        resp = self.client.get(repo_url)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        show_button = json.loads(resp.context['show_export_button_json'])
        self.assertTrue(show_button)

        # Even though the listing page is empty the export button should
        # still show up.
        url = "{repo_url}?q=zebra".format(repo_url=repo_url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        show_button = json.loads(resp.context['show_export_button_json'])
        self.assertTrue(show_button)

        # Export button should only appear if there are LearningResources in
        # the repository.
        LearningResource.objects.all().delete()
        resp = self.client.get(repo_url)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        show_button = json.loads(resp.context['show_export_button_json'])
        self.assertFalse(show_button)
