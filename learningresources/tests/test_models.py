"""
Tests for learningresources models
"""
from __future__ import unicode_literals

from django.test.testcases import TestCase

from learningresources.models import LearningResourceType


class TestModels(TestCase):
    """Tests for learningresources models"""

    def test_unicode(self):
        """Test for __unicode__ on LearningResourceType"""
        first = LearningResourceType.objects.create(
            name="first"
        )

        self.assertEquals("first", str(first))
