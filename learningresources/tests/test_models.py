"""
Tests for learningresources models
"""
from __future__ import unicode_literals

from .base import LoreTestCase
from learningresources.models import LearningResourceType, Repository


class TestModels(LoreTestCase):
    """Tests for learningresources models"""

    def test_unicode(self):
        """Test for __unicode__ on LearningResourceType"""
        first = LearningResourceType.objects.create(
            name="first"
        )

        self.assertEquals("first", str(first))

    def test_repo_slug(self):
        """Test behavior saving a repository slug"""
        repo = Repository.objects.create(
            name="reponame",
            description="description",
            created_by_id=self.user.id,
        )
        self.assertEqual(repo.name, "reponame")
        self.assertEqual(repo.description, "description")
        self.assertEqual(repo.slug, "reponame")

        # slug should remain the same
        repo.save()
        self.assertEqual(repo.name, "reponame")
        self.assertEqual(repo.slug, "reponame")

        repo.name = "repo name"
        repo.save()
        self.assertEqual(repo.name, "repo name")
        self.assertEqual(repo.slug, "repo-name")
