"""
Tests for taxonomy app
"""

# pylint: disable=no-member
# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name
from django.db.transaction import rollback

from django.test.testcases import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningobjects.models import (
    LearningObject,
    LearningObjectType,
    Repository,
    Course,
)
from taxonomy.api import (
    add_term_to_learning_object,
    add_type_for_vocabulary,
    create_term,
    create_vocabulary,
    delete_term,
    delete_vocabulary,
    get_learning_objects_for_term,
    get_term,
    get_terms_for_learning_object,
    get_types_for_vocabulary,
    get_vocabularies_for_type,
    get_vocabulary,
    remove_term_from_learning_object,
    remove_type_from_vocabulary,
    TaxonomyAPIException,
)


class TestApi(TestCase):
    """Tests for taxomony API"""

    def setUp(self):
        super(TestApi, self).setUp()
        self.user = User.objects.create(username="test")

        self.repository = Repository.objects.create(
            create_date="2014-08-08",
            created_by=self.user,
        )

        self.vocabulary = Vocabulary.objects.create(
            repository=self.repository,
            required=False,
            weight=100,
        )

        self.learning_object_type1 = LearningObjectType.objects.create(
            name="Type1",
        )
        self.learning_object_type2 = LearningObjectType.objects.create(
            name="Type2",
        )

        self.course = Course.objects.create(
            repository=self.repository,
            imported_by=self.user,
        )

        self.learning_object = LearningObject.objects.create(
            course=self.course,
            learning_object_type=self.learning_object_type1,
        )

        self.term = Term.objects.create(
            vocabulary=self.vocabulary,
            weight=4,
        )

    def test_add_term_to_learning_object(self):
        """
        Test add_term_to_learning_object
        """
        self.assertEquals(0, self.learning_object.terms.count())
        add_term_to_learning_object(self.learning_object.id, self.term.id)
        self.assertEquals([self.term], list(self.learning_object.terms.all()))
        add_term_to_learning_object(self.learning_object.id, self.term.id)

        # duplicate term is ignored
        self.assertEquals([self.term],
                          list(self.learning_object.terms.all()))

        self.assertRaises(LearningObject.DoesNotExist,
                          lambda: add_term_to_learning_object(
                              -3, self.term.id))
        self.assertRaises(Term.DoesNotExist,
                          lambda: add_term_to_learning_object(
                              self.learning_object.id, -4))
        self.assertRaises(LearningObject.DoesNotExist,
                          lambda: add_term_to_learning_object(
                              None, None))

    def test_add_type_for_vocabulary(self):
        """
        Test add_type_for_vocabulary
        """
        self.assertEquals(0, self.vocabulary.learning_object_types.count())
        add_type_for_vocabulary(self.learning_object_type1.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_object_type1],
                          list(self.vocabulary.learning_object_types.all()))
        add_type_for_vocabulary(self.learning_object_type2.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_object_type1,
                           self.learning_object_type2],
                          list(self.vocabulary.learning_object_types.order_by(
                              'name')))

        # duplicate is ignored
        add_type_for_vocabulary(self.learning_object_type1.name,
                                self.vocabulary.id)
        self.assertEquals([self.learning_object_type1,
                           self.learning_object_type2],
                          list(self.vocabulary.learning_object_types.order_by(
                              'name')))

    def test_create_term(self):
        """
        Test create_term
        """
        self.assertEquals([self.term],
                          list(Term.objects.all()))

        term = create_term(self.vocabulary.id, "label", 9)
        self.assertEquals([self.term, term],
                          list(Term.objects.order_by('id')))

        self.assertRaises(Vocabulary.DoesNotExist,
                          lambda: create_term(456, "label", 9))
        self.assertRaises(IntegrityError,
                          lambda: create_term(self.vocabulary.id, None, 9))
        create_term(self.vocabulary.id, "label2", 99.7)
        # term weight is truncated after being stored in database
        self.assertEquals(1, Term.objects.filter(weight=99).count())

    def test_create_vocabulary(self):
        """
        Test create_vocabulary
        """
        self.assertEquals([self.vocabulary],
                          list(Vocabulary.objects.all()))

        v = create_vocabulary(self.repository.id,
                              "vocabulary",
                              "description",
                              False,
                              "f",
                              9)
        self.assertEquals([self.vocabulary, v],
                          list(Vocabulary.objects.order_by('id')))
        self.assertRaises(Repository.DoesNotExist,
                          lambda: create_vocabulary(9,
                                                    "vocabulary",
                                                    "description",
                                                    False,
                                                    "m",
                                                    9))

        # int is cast to string
        create_vocabulary(self.repository.id,
                          9,
                          "description",
                          False,
                          "f",
                          9)
        self.assertEquals("9", Vocabulary.objects.order_by('id').last().name)

        create_vocabulary(self.repository.id,
                          "name",
                          9,
                          False,
                          "m",
                          9)
        self.assertEquals("9", Vocabulary.objects.order_by('id').
                          last().description)

        # "abc" is cast to boolean True
        create_vocabulary(self.repository.id,
                          "vocabulary",
                          "description",
                          "abc",
                          "f",
                          9)
        self.assertEquals(True, Vocabulary.objects.order_by('id').last().
                          required)

        # pass in None, violates constraints
        self.assertRaises(IntegrityError,
                          lambda: create_vocabulary(self.repository.id,
                                                    "vocabulary",
                                                    "description",
                                                    None,
                                                    "m",
                                                    9))

        self.assertRaises(TaxonomyAPIException,
                          lambda: create_vocabulary(self.repository.id,
                                                    "vocabulary",
                                                    "description",
                                                    False,
                                                    ";",
                                                    9))

    def test_delete_term(self):
        """
        Test delete_term
        """
        self.assertEquals(1, Term.objects.count())
        delete_term(self.term.id)
        self.assertEquals(0, Term.objects.count())
        delete_term(9)
        delete_term(self.term.id)
        self.assertEquals(0, Term.objects.count())

    def test_delete_vocabulary(self):
        """
        Test delete_vocabulary
        """
        self.assertEquals(1, Vocabulary.objects.count())
        delete_vocabulary(9)
        self.assertEquals(1, Vocabulary.objects.count())
        delete_vocabulary(self.vocabulary.id)
        self.assertEquals(0, Vocabulary.objects.count())

    def test_get_learning_objects_for_term(self):
        """
        Test get_learning_objects_for_term
        """
        self.assertEquals([],
                          list(get_learning_objects_for_term(self.term.id)))

        self.learning_object.terms.add(self.term)
        self.assertEquals([self.learning_object],
                          list(get_learning_objects_for_term(self.term.id)))

        self.assertRaises(Term.DoesNotExist,
                          lambda: get_learning_objects_for_term(9))

    def test_get_term(self):
        """
        Test get_term
        """
        self.assertRaises(Term.DoesNotExist, lambda: get_term(9))
        self.assertEquals(self.term, get_term(self.term.id))

    def test_get_terms_for_learning_object(self):
        """
        Test get_terms_for_learning_object
        """
        self.assertEquals([],
                          list(get_terms_for_learning_object(
                              self.learning_object.id)))

        self.term.learning_objects.add(self.learning_object)
        self.assertEquals([self.term],
                          list(get_terms_for_learning_object(
                              self.learning_object.id)))
        self.assertRaises(LearningObject.DoesNotExist,
                          lambda: get_terms_for_learning_object(9))

    def test_get_types_for_vocabulary(self):
        """
        Test get_types_for_vocabulary
        """
        self.assertEquals([self.learning_object_type1.name],
                          [t.name for t in
                           get_types_for_vocabulary(self.vocabulary.id)])
        self.assertRaises(Vocabulary.DoesNotExist,
                          lambda: get_types_for_vocabulary(3))

    def test_get_vocabularies_for_type(self):
        """
        Test get_vocabularies_for_type
        """
        self.assertEquals([self.vocabulary],
                          list(get_vocabularies_for_type(
                              self.learning_object_type1.name)))
        self.assertRaises(LearningObjectType.DoesNotExist,
                          lambda: get_vocabularies_for_type("xyz"))

    def test_get_vocabulary(self):
        """
        Test get_vocabulary
        """

        actual_vocabulary = get_vocabulary(self.vocabulary.id)
        self.assertEquals(self.vocabulary, actual_vocabulary)

        self.assertRaises(Vocabulary.DoesNotExist,
                          lambda: get_vocabulary(3))
        self.assertRaises(Vocabulary.DoesNotExist,
                          lambda: get_vocabulary(None))

    def test_remove_term_from_learning_object(self):
        """
        Test remove_term_from_learning_object
        """
        self.assertEquals([self.term],
                          get_terms_for_learning_object(
                              self.learning_object.id))
        remove_term_from_learning_object(self.term.id, self.learning_object.id)
        self.assertEquals([],
                          get_terms_for_learning_object(
                              self.learning_object.id))

    def test_remove_type_from_vocabulary(self):
        """
        Test remove_type_from_vocabulary
        """
        self.assertEquals([self.vocabulary.id],
                          get_vocabularies_for_type(
                              self.learning_object_type1.name))
        remove_type_from_vocabulary(self.learning_object_type1.name,
                                    self.vocabulary.id)
        self.assertEquals([],
                          get_vocabularies_for_type(
                              self.learning_object_type1.name))

        remove_type_from_vocabulary(self.learning_object_type1.name,
                                    self.vocabulary.id)
        remove_type_from_vocabulary("xyz", self.vocabulary.id)
