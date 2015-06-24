"""
Tests for taxonomy app
"""
from __future__ import unicode_literals

# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name

from learningresources.tests.base import LoreTestCase
from learningresources.api import (
    NotFound,
    PermissionDenied,
)

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningresources.models import (
    LearningResource,
    LearningResourceType,
    Course,
)
from taxonomy.api import (
    get_term,
    get_vocabulary,
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

    def test_get_term(self):
        """
        Test get_term
        """
        actual_term = get_term(
            self.repo.slug,
            self.user.id,
            self.vocabulary.slug,
            self.term.slug
        )
        self.assertEquals(self.term, actual_term)
        with self.assertRaises(NotFound):
            get_term('missing', self.user.id,
                     self.vocabulary.slug, self.term.slug)
        with self.assertRaises(PermissionDenied):
            get_term(self.repo.slug, -1,
                     self.vocabulary.slug, self.term.slug)
        with self.assertRaises(NotFound):
            get_term(self.repo.slug, self.user.id,
                     'missing', self.term.slug)
        with self.assertRaises(NotFound):
            get_term(self.repo.slug, self.user.id,
                     self.vocabulary.slug, 'missing')

    def test_get_vocabulary(self):
        """
        Test get_vocabulary
        """

        actual_vocabulary = get_vocabulary(
            self.repo.slug, self.user.id, self.vocabulary.slug)
        self.assertEquals(self.vocabulary, actual_vocabulary)

        with self.assertRaises(NotFound):
            get_vocabulary("missing", self.user.id, self.vocabulary.slug)
        with self.assertRaises(PermissionDenied):
            get_vocabulary(self.repo.slug, -1, self.vocabulary.slug)
        with self.assertRaises(NotFound):
            get_vocabulary(self.repo.slug, self.user.id, "missing")
