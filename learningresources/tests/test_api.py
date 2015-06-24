"""
Test api functions.
"""

from __future__ import unicode_literals

import logging

from django.db.utils import IntegrityError

from learningresources.api import (
    get_repo, get_repos,
    NotFound, PermissionDenied,
)
from learningresources.models import Course, LearningResource
from learningresources.api import create_course, get_resource, create_repo
from importer.api import import_course_from_file

from .base import LoreTestCase

log = logging.getLogger(__name__)


class TestCreateCourse(LoreTestCase):
    """
    Test course creation API.
    """
    def setUp(self):
        """
        Set some test data
        """
        super(TestCreateCourse, self).setUp()
        self.kwargs = {
            'org': 'demo org',
            'course_number': '42',
            'run': 'Febtober',
            'user_id': self.user.id,
            'repo_id': self.repo.id,
        }

    def tearDown(self):
        """
        Clean up test data.
        """
        super(TestCreateCourse, self).tearDown()
        kwargs = self.kwargs
        kwargs["repository_id"] = kwargs["repo_id"]
        kwargs.pop("user_id")
        kwargs.pop("repo_id")
        Course.objects.filter(**kwargs).delete()

    def test_create(self):
        """
        Create a course.
        """
        before = course_count()
        course = create_course(**self.kwargs)
        after = course_count()
        self.assertTrue(after == before + 1)
        self.assertTrue(course is not None)

        # Can't create a duplicate.
        with self.assertRaises(ValueError):
            create_course(**self.kwargs)
        self.assertTrue(course_count() == after)

        # NOT NULL constraint fails on org
        with self.assertRaises(IntegrityError) as ex:
            create_course(None, self.repo.id, "course", "run", self.user.id)

        self.assertIn("org", ex.exception.args[0])


class TestResources(LoreTestCase):
    """Test LearningResource functions."""

    def setUp(self):
        """
        Set some test data
        """
        super(TestResources, self).setUp()
        import_course_from_file(
            self.get_course_single_tarball(), self.repo.id, self.user.id)

    def test_get_resource(self):
        """Get a resource"""
        resource_id = LearningResource.objects.all()[0].id
        self.assertTrue(
            isinstance(
                get_resource(resource_id, self.user.id),
                LearningResource
            )
        )

    def test_get_missing_resource(self):
        """Get a resource"""
        resource_id = LearningResource.objects.all().order_by("-id")[0].id + 1
        with self.assertRaises(NotFound):
            get_resource(resource_id, self.user.id)

    def test_get_no_permission_resource(self):
        """Get a resource"""
        resource_id = LearningResource.objects.all()[0].id
        with self.assertRaises(PermissionDenied):
            get_resource(resource_id, self.user_norepo.id)


class TestRepoAPI(LoreTestCase):
    """
    Tests repo getters
    """
    def test_get_repo(self):
        """repo does not exist"""
        # this should not fail
        get_repo(self.repo.slug, self.user.id)
        self.assertRaises(
            NotFound,
            get_repo,
            "nonexistent_repo",
            self.user.id
        )
        self.assertRaises(
            PermissionDenied,
            get_repo,
            self.repo.slug,
            self.user_norepo.id
        )

    def test_get_repos(self):
        """test get_repos"""
        self.assertEqual([self.repo],
                         list(get_repos(self.user.id)))
        self.assertEqual([],
                         list(get_repos(self.user_norepo.id)))
        with self.assertRaises(PermissionDenied):
            get_repos(-1)

    def test_invalid_create_repo(self):
        """Create a repository with empty name and description"""
        with self.assertRaises(IntegrityError) as ex:
            create_repo(None, "description", self.user.id)
        self.assertIn("name", ex.exception.args[0])

        with self.assertRaises(IntegrityError) as ex:
            create_repo("name", None, self.user.id)
        self.assertIn("description", ex.exception.args[0])


def course_count():
    """
    Return number of courses in the database.
    """
    return Course.objects.count()
