"""
Tests for utilities within the API.
"""

import logging

from learningresources.tests.base import LoreTestCase

from learningresources.api import update_xanalytics
from learningresources.models import LearningResource

log = logging.getLogger(__name__)


class TestXanalyticsData(LoreTestCase):
    """
    Test good and bad data.
    """
    def test_good(self):
        """Reasonable data."""
        self.resource.uuid = "1"
        self.resource.save()
        resource = LearningResource.objects.get(id=self.resource.id)

        self.assertEqual(resource.xa_nr_views, 0)
        self.assertEqual(resource.xa_nr_attempts, 0)

        reasonable = {
            "course_id": self.course.course_number,
            "module_medata": [
                {
                    "module_id": "1",
                    "xa_nr_views": "3",
                    "xa_nr_attempts": "25"
                },
            ]
        }

        self.assertEqual(update_xanalytics(reasonable), 1)
        resource = LearningResource.objects.get(id=self.resource.id)
        self.assertEqual(resource.xa_nr_views, 3)
        self.assertEqual(resource.xa_nr_attempts, 25)

    def test_empty(self):
        """Empty dict."""
        self.assertEqual(update_xanalytics({}), 0)

    def test_course_id(self):
        """Missing/bad course ID."""
        data = {
            "module_medata": [
                {
                    "module_id": "1",
                    "xa_nr_views": "3",
                    "xa_nr_attempts": "25"
                },
            ]
        }
        self.assertEqual(update_xanalytics(data), 0)
