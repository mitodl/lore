"""
Tests for taxonomy app
"""

import unittest
import pytest

from django.contrib.auth.models import (
    User,
)

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningobjects.models import (
    LearningObject,
    LearningObjectType,
    Repository,
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


class TestApi(unittest.TestCase):
    """Tests for taxomony API"""

    @pytest.mark.django_db
    def test_get_vocabulary(self):
        """
        Test get_vocabulary
        """

        user = User()
        user.save()

        repository = Repository.objects.create(
            create_date="2014-08-08",
            created_by=user,
        )

        expected_vocabulary = Vocabulary.objects.create(
            repository=repository,
            required=False,
            weight=100,
        )

        actual_vocabulary = get_vocabulary(expected_vocabulary.id)
        self.assertEquals(expected_vocabulary, actual_vocabulary)
