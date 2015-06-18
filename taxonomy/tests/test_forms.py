"""
Tests for taxonomy forms
"""
from __future__ import unicode_literals

from django.db.utils import IntegrityError
from django.db import transaction

from ui.forms import VocabularyForm
from taxonomy.models import Vocabulary
from learningresources.models import LearningResourceType
from importer.api import import_course_from_file

from learningresources.models import Repository
from learningresources.tests.base import LoreTestCase


class TestForms(LoreTestCase):
    """Tests for taxomony forms"""

    def setUp(self):
        """
        Initialize
        """
        super(TestForms, self).setUp()
        import_course_from_file(
            self.get_course_zip(), self.repo.id, self.user.id
        )

        self.video_type, _ = LearningResourceType.objects.get_or_create(
            name="video")

    def test_new(self):
        """
        Create a new vocabulary
        """

        form = VocabularyForm({
            'name': 'name',
            'description': 'description',
            'vocabulary_type': Vocabulary.FREE_TAGGING,
            'learning_resource_types': [self.video_type.id],
        })
        form.instance.repository = Repository.objects.order_by('id').first()
        form.instance.required = False
        form.instance.weight = 1000
        self.assertEquals(0, Vocabulary.objects.count())
        form.save()
        self.assertEquals(1, Vocabulary.objects.count())

        form = VocabularyForm({
            'name': 'name',
            'description': 'description',
            'vocabulary_type': Vocabulary.FREE_TAGGING,
            'learning_resource_types': [self.video_type.id],
        })
        form.instance.repository = Repository.objects.order_by('id').first()
        form.instance.required = False
        form.instance.weight = 1000

        # duplicate save should fail on unique constraint
        # pylint: disable=unnecessary-lambda
        with transaction.atomic():
            self.assertRaises(IntegrityError, lambda: form.save())
        self.assertEquals(1, Vocabulary.objects.count())

    def test_update(self):
        """
        Update vocabulary via form
        """
        vocab = Vocabulary.objects.create(
            repository=Repository.objects.order_by('id').first(),
            name='name',
            description='description',
            required=True,
            vocabulary_type=Vocabulary.MANAGED,
            weight=100,
        )

        self.assertEquals('name', vocab.name)
        self.assertEquals('name', vocab.slug)
        self.assertEquals(Vocabulary.MANAGED, vocab.vocabulary_type)
        self.assertEquals(0, vocab.learning_resource_types.count())
        self.assertEquals(True, vocab.required)

        form = VocabularyForm({
            'name': 'edited name',
            'description': 'description',
            'vocabulary_type': Vocabulary.FREE_TAGGING,
            'learning_resource_types': [self.video_type.id],
        }, instance=vocab)
        form.save()

        vocab = Vocabulary.objects.get(id=vocab.id)
        self.assertEquals('edited name', vocab.name)
        self.assertEquals('edited-name', vocab.slug)
        self.assertEquals(Vocabulary.FREE_TAGGING, vocab.vocabulary_type)
        self.assertEquals(1, vocab.learning_resource_types.count())
        self.assertEquals(True, vocab.required)
