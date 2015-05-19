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

        self.repository = Repository.objects.create(
            created_by=self.user,
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
        self.assertRaises(Vocabulary.DoesNotExist,
                          lambda: create_term(self.vocabulary.id, "label2",
                                              4.5))

    def test_create_vocabulary(self):
        """
        Test create_vocabulary
        """

    def test_delete_term(self):
        """
        Test delete_term
        """

    def test_delete_vocabulary(self):
        """
        Test delete_vocabulary
        """

    def test_get_learning_objects_for_term(self):
        """
        Test get_learning_objects_for_term
        """

    def test_get_term(self):
        """
        Test get_term
        """

    def test_get_terms_for_learning_object(self):
        """
        Test get_terms_for_learning_object
        """

    def test_get_types_for_vocabulary(self):
        """
        Test get_types_for_vocabulary
        """

    def test_get_vocabularies_for_type(self):
        """
        Test get_vocabularies_for_type
        """

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

    def test_remove_type_from_vocabulary(self):
        """
        Test remove_type_from_vocabulary
        """
