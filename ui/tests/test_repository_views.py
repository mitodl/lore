"""
Tests for repository views
"""

from __future__ import unicode_literals

from learningresources.tests.base import LoreTestCase
from learningresources.models import LearningResource


class TestViews(LoreTestCase):
    """Test repository view."""

    def test_export_button(self):
        """Make sure export button is visible at the appropriate times."""
        button_text = '<button id="export_button"'
        repo_url = '/repositories/{repo}/'.format(repo=self.repo.slug)
        resp = self.client.get(repo_url)
        self.assertContains(resp, button_text)

        # Export button should only appear if there are LearningResources in
        # the repository.
        LearningResource.objects.all().delete()
        resp = self.client.get(repo_url)
        self.assertNotContains(resp, button_text)
