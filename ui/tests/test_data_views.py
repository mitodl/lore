"""
Test views for data grid view of learning resources.
"""

from __future__ import unicode_literals

from learningresources.tests.base import LoreTestCase


class TestDataViews(LoreTestCase):
    """
    Test views for data grid view of learning resources.
    """
    def test_repo(self):
        """
        Test that repo is present.
        """
        resp = self.client.get(
            "/repositories/{slug}/data/".format(slug=self.repo.slug))
        self.assertEqual(self.repo, resp.context['repo'])
