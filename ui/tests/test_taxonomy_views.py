"""Tests for taxonomy views"""

from __future__ import unicode_literals

from learningresources.tests.base import LoreTestCase
from learningresources.models import LearningResourceType
from taxonomy.models import Vocabulary
from taxonomy.api import create_vocabulary

HTTP_OK = 200
NOT_FOUND = 404


class TestViews(LoreTestCase):
    """Test views for taxonomy app"""
    def setUp(self):
        super(TestViews, self).setUp()

        LearningResourceType.objects.create(name="type1")

    def test_create_vocabulary(self):
        """Test new vocabulary page"""
        # look at empty create page
        resp = self.client.get(
            "/repositories/{repo_slug}/vocabularies".format(
                repo_slug=self.repo.slug
            ), follow=True)
        self.assertEquals(HTTP_OK, resp.status_code)
        body = resp.content.decode('utf-8')
        self.assertIn("Describe how content authors", body)

        # post empty form to create new vocabulary. Shouldn't work
        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/".format(
                repo_slug=self.repo.slug
            ), {}, follow=True)
        # form was invalid but page should still be 200
        self.assertEqual(HTTP_OK, resp.status_code)
        self.assertIn("Describe how content authors", body)
        # no taxonomies should be created since form was invalid
        self.assertEquals(0, Vocabulary.objects.count())

        # post a valid form
        lrt = LearningResourceType.objects.first()
        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/".format(
                repo_slug=self.repo.slug
            ), {
                'name': 'vocab 1',
                'description': 'description 1',
                'learning_resource_types': lrt.id,
                'vocabulary_type': Vocabulary.FREE_TAGGING
            }, follow=True)
        self.assertEquals(HTTP_OK, resp.status_code)
        self.assertEquals(1, Vocabulary.objects.count())

        vocab = Vocabulary.objects.first()
        self.assertEquals('vocab 1', vocab.name)
        self.assertEquals('description 1', vocab.description)
        self.assertEquals([lrt], list(vocab.learning_resource_types.all()))

    def test_edit_vocabulary(self):
        """Edit an existing vocabulary"""

        self.assertEqual(0, Vocabulary.objects.count())

        resp = self.client.get(
            "/repositories/{repo_slug}/vocabularies/345".format(
                repo_slug=self.repo.slug
            ),
            follow=True
        )
        self.assertEqual(NOT_FOUND, resp.status_code)

        vocab = create_vocabulary(
            self.repo.id,
            "XY Z",
            "ABC",
            False,
            Vocabulary.MANAGED,
            100
        )

        resp = self.client.get("/repositories/999/vocabularies", follow=True)
        self.assertEqual(NOT_FOUND, resp.status_code)

        resp = self.client.get(
            "/repositories/{repo_slug}/vocabularies/{vocab_slug}".format(
                repo_slug=self.repo.slug,
                vocab_slug=vocab.slug,
            ), follow=True)
        self.assertEqual(HTTP_OK, resp.status_code)
        body = resp.content.decode('utf-8')
        self.assertIn(vocab.name, body)
        self.assertIn(vocab.description, body)
        self.assertEqual(0, vocab.learning_resource_types.count())
        self.assertEqual(1, Vocabulary.objects.count())

        # edit existing vocabulary but keep the same name
        lrt = LearningResourceType.objects.first()
        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/{vocab_slug}/".format(
                repo_slug=self.repo.slug,
                vocab_slug=vocab.slug,
            ), {
                'name': vocab.name,
                'description': 'description 2',
                'learning_resource_types': lrt.id,
                'vocabulary_type': Vocabulary.FREE_TAGGING
            }, follow=True)
        self.assertEqual(HTTP_OK, resp.status_code)
        vocab = Vocabulary.objects.first()
        # no new vocabularies
        self.assertEqual(1, Vocabulary.objects.count())
        self.assertEqual("XY Z", vocab.name)
        self.assertEqual("xy-z", vocab.slug)
        self.assertEqual("description 2", vocab.description)
        self.assertEqual(Vocabulary.FREE_TAGGING, vocab.vocabulary_type)

        # edit existing vocabulary and change the name
        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/{vocab_slug}/".format(
                repo_slug=self.repo.slug,
                vocab_slug=vocab.slug,
            ), {
                'name': "new name",
                'description': 'description 2',
                'learning_resource_types': lrt.id,
                'vocabulary_type': Vocabulary.FREE_TAGGING
            }, follow=True)
        self.assertEqual(HTTP_OK, resp.status_code)
        # still no new vocabularies
        self.assertEqual(1, Vocabulary.objects.count())
        self.assertEqual("new name", Vocabulary.objects.first().name)

        # get a 404 when we POST to a non-existing vocabulary
        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/{vocab_slug}/".format(
                repo_slug=self.repo.slug,
                vocab_slug="987",
            ), {
                'name': "new name",
                'description': 'description 2',
                'learning_resource_types': lrt.id,
                'vocabulary_type': Vocabulary.FREE_TAGGING
            }, follow=True)
        self.assertEqual(NOT_FOUND, resp.status_code)

        # validate that some learning resource type needs to be specified
        self.assertEqual(1, Vocabulary.objects.count())
        vocab = Vocabulary.objects.first()

        resp = self.client.post(
            "/repositories/{repo_slug}/vocabularies/{vocab_slug}/".format(
                repo_slug=self.repo.slug,
                vocab_slug=vocab.slug,
            ), {
                'name': "new name",
                'description': 'description 2',
                'vocabulary_type': Vocabulary.FREE_TAGGING
            }, follow=True)
        self.assertEqual(HTTP_OK, resp.status_code)

        self.assertEqual(1, Vocabulary.objects.count())
        self.assertEqual(
            [lrt],
            list(Vocabulary.objects.first().learning_resource_types.all())
        )
