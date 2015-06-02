"""
Tests for taxonomy app
"""
from __future__ import unicode_literals

# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name

from django.http.response import Http404
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from learningresources.tests.base import LoreTestCase

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningresources.models import (
    LearningResource,
    LearningResourceType,
    Course,
)
from learningresources.api import create_repo
from taxonomy.api import (
    add_term_to_learning_resource,
    add_type_for_vocabulary,
    create_term,
    create_vocabulary,
    delete_term,
    delete_vocabulary,
    get_learning_resources_for_term,
    get_term,
    get_terms_for_learning_resource,
    get_types_for_vocabulary,
    get_vocabularies_for_type,
    get_vocabulary,
    remove_term_from_learning_resource,
    remove_type_from_vocabulary,
)


class TestApi(LoreTestCase):
    """Tests for taxomony API"""

    def setUp(self):
        super(TestApi, self).setUp()

        self.vocabulary = Vocabulary.objects.create(
            repository=self.repo,
            required=False,
            weight=100,
        )

        self.learning_resource_type1 = LearningResourceType.objects.create(
            name="Type1",
        )
        self.learning_resource_type2 = LearningResourceType.objects.create(
            name="Type2",
        )

        self.course = Course.objects.create(
            repository=self.repo,
            imported_by=self.user,
        )

        self.learning_resource = LearningResource.objects.create(
            course=self.course,
            learning_resource_type=self.learning_resource_type1,
        )

        self.term = Term.objects.create(
            vocabulary=self.vocabulary,
            weight=4,
        )

    def test_add_term_to_learning_resource(self):
        """
        Test add_term_to_learning_resource
        """
        self.assertEquals(0, self.learning_resource.terms.count())
        add_term_to_learning_resource(self.learning_resource.id, self.term.id)
        self.assertEquals([self.term],
                          list(self.learning_resource.terms.all()))
        add_term_to_learning_resource(self.learning_resource.id, self.term.id)

        # duplicate term is ignored
        self.assertEquals([self.term],
                          list(self.learning_resource.terms.all()))

        self.assertRaises(Http404,
                          lambda: add_term_to_learning_resource(
                              -3, self.term.id))
        self.assertRaises(Http404,
                          lambda: add_term_to_learning_resource(
                              self.learning_resource.id, -4))
        self.assertRaises(Http404,
                          lambda: add_term_to_learning_resource(
                              None, None))

    def test_add_type_for_vocabulary(self):
        """
        Test add_type_for_vocabulary
        """
        self.assertEquals(0, self.vocabulary.learning_resource_types.count())
        add_type_for_vocabulary(self.learning_resource_type1.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_resource_type1],
                          list(self.vocabulary.learning_resource_types.all()))
        add_type_for_vocabulary(self.learning_resource_type2.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_resource_type1,
                           self.learning_resource_type2],
                          list(
                              self.vocabulary.learning_resource_types.
                              order_by('name')))

        # duplicate is ignored
        add_type_for_vocabulary(self.learning_resource_type1.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_resource_type1,
                           self.learning_resource_type2],
                          list(
                              self.vocabulary.learning_resource_types.
                              order_by('name')))

    def test_create_term(self):
        """
        Test create_term
        """
        self.assertEquals([self.term],
                          list(Term.objects.all()))

        term = create_term(self.vocabulary.id, "label", 9)
        self.assertEquals([self.term, term],
                          list(Term.objects.order_by('id')))

        self.assertRaises(ValidationError,
                          lambda: create_term(456, "label", 9))
        self.assertRaises(ValidationError,
                          lambda: create_term(self.vocabulary.id, None, 9))

    def test_create_vocabulary(self):
        """
        Test create_vocabulary
        """
        self.assertEquals([self.vocabulary],
                          list(Vocabulary.objects.all()))

        vocabulary = create_vocabulary(self.repo.id,
                                       "vocabulary",
                                       "description",
                                       False,
                                       Vocabulary.FREE_TAGGING,
                                       9)
        self.assertEquals([self.vocabulary, vocabulary],
                          list(Vocabulary.objects.order_by('id')))

        other_repository = create_repo(
            "other repository",
            "description",
            self.user.id,
        )

        vocabulary_1 = create_vocabulary(
            other_repository.id,
            "vocabulary",
            "description",
            False,
            Vocabulary.FREE_TAGGING,
            9)
        # the slug is different
        self.assertNotEqual(vocabulary, vocabulary_1)
        self.assertEqual("vocabulary1", vocabulary_1.slug)
        self.assertRaises(ValidationError,
                          lambda: create_vocabulary(9,
                                                    "vocabulary",
                                                    "description",
                                                    False,
                                                    Vocabulary.MANAGED,
                                                    9))

        self.assertRaises(ValidationError,
                          lambda: create_vocabulary(self.repo.id,
                                                    "vocabulary",
                                                    "description",
                                                    "abc",
                                                    Vocabulary.FREE_TAGGING,
                                                    9))

        # pass in None, violates constraints
        self.assertRaises(ValidationError,
                          lambda: create_vocabulary(self.repo.id,
                                                    "vocabulary",
                                                    "description",
                                                    None,
                                                    Vocabulary.MANAGED,
                                                    9))

        self.assertRaises(ValidationError,
                          lambda: create_vocabulary(self.repo.id,
                                                    "vocabulary",
                                                    "description",
                                                    False,
                                                    "",
                                                    9))

    def test_delete_term(self):
        """
        Test delete_term
        """
        self.assertEquals(1, Term.objects.count())
        delete_term(self.term.id)
        self.assertEquals(0, Term.objects.count())
        self.assertRaises(Http404, lambda: delete_term(9))
        self.assertRaises(Http404, lambda: delete_term(self.term.id))
        self.assertEquals(0, Term.objects.count())

    def test_delete_vocabulary(self):
        """
        Test delete_vocabulary
        """
        self.assertEquals(1, Vocabulary.objects.count())
        self.assertRaises(Http404, lambda: delete_vocabulary(9))
        self.assertEquals(1, Vocabulary.objects.count())
        self.assertRaises(ProtectedError, lambda: delete_vocabulary(
            self.vocabulary.id))
        delete_term(self.term.id)
        delete_vocabulary(self.vocabulary.id)
        self.assertEquals(0, Vocabulary.objects.count())

    def test_get_learning_resources_for_term(self):
        """
        Test get_learning_resources_for_term
        """
        self.assertEquals([],
                          list(get_learning_resources_for_term(self.term.id)))

        self.learning_resource.terms.add(self.term)
        self.assertEquals([self.learning_resource],
                          list(get_learning_resources_for_term(self.term.id)))

        self.assertRaises(Http404,
                          lambda: get_learning_resources_for_term(9))

    def test_get_term(self):
        """
        Test get_term
        """
        invalid_id = -1
        self.assertRaises(Http404, lambda: get_term(invalid_id))
        self.assertEquals(self.term, get_term(self.term.id))

    def test_get_terms_for_learning_resource(self):
        """
        Test get_terms_for_learning_resource
        """
        self.assertEquals([],
                          list(get_terms_for_learning_resource(
                              self.learning_resource.id)))

        self.term.learning_resources.add(self.learning_resource)
        self.assertEquals([self.term],
                          list(get_terms_for_learning_resource(
                              self.learning_resource.id)))
        self.assertRaises(Http404,
                          lambda: get_terms_for_learning_resource(9))

    def test_get_types_for_vocabulary(self):
        """
        Test get_types_for_vocabulary
        """
        self.vocabulary.learning_resource_types.add(
            self.learning_resource_type1)
        self.assertEquals([self.learning_resource_type1.name],
                          list(get_types_for_vocabulary(self.vocabulary.id)))
        self.assertRaises(Http404,
                          lambda: get_types_for_vocabulary(3))

    def test_get_vocabularies_for_type(self):
        """
        Test get_vocabularies_for_type
        """
        self.vocabulary.learning_resource_types.add(
            self.learning_resource_type1)
        self.assertEquals([self.vocabulary],
                          list(get_vocabularies_for_type(
                              self.learning_resource_type1.name)))
        self.assertRaises(Http404,
                          lambda: get_vocabularies_for_type("xyz"))

    def test_get_vocabulary(self):
        """
        Test get_vocabulary
        """

        actual_vocabulary = get_vocabulary(self.vocabulary.id)
        self.assertEquals(self.vocabulary, actual_vocabulary)

        self.assertRaises(Http404,
                          lambda: get_vocabulary(3))
        self.assertRaises(Http404,
                          lambda: get_vocabulary(None))

    def test_remove_term_from_learning_resource(self):
        """
        Test remove_term_from_learning_resource
        """
        self.learning_resource.terms.add(self.term)
        self.assertEquals([self.term],
                          list(get_terms_for_learning_resource(
                              self.learning_resource.id)))
        remove_term_from_learning_resource(self.learning_resource.id,
                                           self.term.id)
        self.assertEquals([],
                          list(get_terms_for_learning_resource(
                              self.learning_resource.id)))

    def test_remove_type_from_vocabulary(self):
        """
        Test remove_type_from_vocabulary
        """
        self.vocabulary.learning_resource_types.add(
            self.learning_resource_type1)

        self.assertEquals([self.vocabulary],
                          list(get_vocabularies_for_type(
                              self.learning_resource_type1.name)))
        remove_type_from_vocabulary(self.learning_resource_type1.name,
                                    self.vocabulary.id)
        self.assertEquals([],
                          list(get_vocabularies_for_type(
                              self.learning_resource_type1.name)))

        remove_type_from_vocabulary(self.learning_resource_type1.name,
                                    self.vocabulary.id)
        self.assertRaises(Http404,
                          lambda: remove_type_from_vocabulary(
                              "xyz", self.vocabulary.id))
