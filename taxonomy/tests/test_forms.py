"""
Tests for taxonomy forms
"""
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test.testcases import TestCase

from taxonomy.forms import VocabularyForm
from taxonomy.models import Vocabulary
from learningresources.models import LearningResourceType
from importer.api import import_course_from_file
from importer.tests.test_import import get_course_zip


class TestForms(TestCase):
    """Tests for taxomony forms"""

    def setUp(self):
        """
        Initialize
        """
        self.user, _ = User.objects.get_or_create(username="test")

        import_course_from_file(get_course_zip(), self.user.id)

    def test_new(self):
        """
        Create a new vocabulary
        """

        form = VocabularyForm({
            'name': 'name',
            'description': 'description',
            'learning_resource_types': [
                LearningResourceType.objects.first().id
            ],
            'vocabulary_type': Vocabulary.FREE_TAGGING,
        })
        form.save()
