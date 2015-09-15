"""
Tests for taxonomy models
"""

from __future__ import unicode_literals

import logging

from taxonomy.models import Vocabulary
from learningresources.api import create_repo, create_resource
from learningresources.tests.base import LoreTestCase

log = logging.getLogger(__name__)


def get_vocabularies(repository_id):
    """
    Get all vocabularies for a repository.
    Args:
        repository_id (int): primary key of Repository
    Returns:
        repositories (list of Vocabulary)
    """
    return [x for x in Vocabulary.objects.filter(repository__id=repository_id)]


class TestModels(LoreTestCase):
    """Tests for taxonomy models"""

    def test_slug(self):
        """Test behavior saving vocabulary slug"""
        vocab = Vocabulary.objects.create(
            repository=self.repo,
            name="vocabname",
            description="description",
            required=False,
            vocabulary_type=Vocabulary.MANAGED,
            weight=1
        )
        self.assertEqual(vocab.name, "vocabname")
        self.assertEqual(vocab.description, "description")
        self.assertEqual(vocab.slug, "vocabname")

        # slug should remain the same
        vocab.save()
        self.assertEqual(vocab.name, "vocabname")
        self.assertEqual(vocab.slug, "vocabname")

        vocab.name = "vocab name"
        vocab.save()
        self.assertEqual(vocab.name, "vocab name")
        self.assertEqual(vocab.slug, "vocab-name")


class TestCuratorVocabulary(LoreTestCase):
    """
    Tests for automatically-created vocabularies.
    """
    def test_vocab_created(self):
        """
        At the moment there are no vocabularies automatically created
        though that will change soon.
        """
        repo = create_repo(
            name="Ford Prefect",
            description="Mostly harmless.",
            user_id=self.user.id
        )
        self.assertEqual(len(get_vocabularies(repo.id)), 0)

    def test_new_resource(self):
        """
        When a new LearningResource is created, it will have no
        terms assigned to it.
        """
        resource = create_resource(
            course=self.course,
            parent=None,
            resource_type="problem",
            title="newly created",
            content_xml="<xml/>",
            mpath="",
            url_name="",
            dpath="",
        )
        terms = resource.terms.all()
        self.assertEqual(terms.count(), 0)
