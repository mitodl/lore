"""
Tests for search API functions.
"""

from __future__ import unicode_literals

from importer.tasks import import_file
from learningresources.api import create_repo
from search.api import construct_queryset
from search.tests.base import SearchTestCase


class TestAPI(SearchTestCase):
    """Test API."""

    def import_course_tarball(self, repo):
        """
        Import course into repository.
        """
        tarball_file = self.get_course_single_tarball()
        import_file(tarball_file, repo.id, self.user.id)

    def test_repository_exact_match(self):
        """
        Test that repository slug matches exactly
        """
        test_repo = create_repo("test", "testing", self.user.id)
        testing_repo = create_repo("testing", "testing", self.user.id)

        # Should start off with nothing in testing_repo.
        self.assertEqual(construct_queryset(test_repo.slug).count(), 0)
        self.assertEqual(construct_queryset(testing_repo.slug).count(), 0)
        self.import_course_tarball(test_repo)

        # We imported into 'test' so 'testing' shouldn't contain anything.
        self.assertTrue(construct_queryset(test_repo.slug).count() > 0)
        self.assertEqual(construct_queryset(testing_repo.slug).count(), 0)
