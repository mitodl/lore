"""
Test api functions.
"""

from __future__ import unicode_literals

import logging

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.db.utils import IntegrityError
import tempfile

from importer.api import import_course_from_file
from learningresources import api
from learningresources.models import (
    Course,
    LearningResource,
    static_asset_basepath,
)
from mock import patch
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
        course = api.create_course(**self.kwargs)
        after = course_count()
        self.assertTrue(after == before + 1)
        self.assertTrue(course is not None)

        # Can't create a duplicate.
        with self.assertRaises(ValueError):
            api.create_course(**self.kwargs)
        self.assertTrue(course_count() == after)

        # NOT NULL constraint fails on org
        with self.assertRaises(IntegrityError) as ex:
            api.create_course(
                None, self.repo.id, "course", "run", self.user.id)

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
                api.get_resource(resource_id, self.user.id),
                LearningResource
            )
        )

    def test_get_missing_resource(self):
        """Get a resource"""
        resource_id = LearningResource.objects.all().order_by("-id")[0].id + 1
        with self.assertRaises(api.NotFound):
            api.get_resource(resource_id, self.user.id)

    def test_get_no_permission_resource(self):
        """Get a resource"""
        resource_id = LearningResource.objects.all()[0].id
        with self.assertRaises(api.PermissionDenied):
            api.get_resource(resource_id, self.user_norepo.id)


class TestRepoAPI(LoreTestCase):
    """
    Tests repo getters
    """
    def test_get_repo(self):
        """repo does not exist"""
        # this should not fail
        api.get_repo(self.repo.slug, self.user.id)
        self.assertRaises(
            api.NotFound,
            api.get_repo,
            "nonexistent_repo",
            self.user.id
        )
        self.assertRaises(
            api.PermissionDenied,
            api.get_repo,
            self.repo.slug,
            self.user_norepo.id
        )

    def test_get_repos(self):
        """test get_repos"""
        self.assertEqual([self.repo],
                         list(api.get_repos(self.user.id)))
        self.assertEqual([],
                         list(api.get_repos(self.user_norepo.id)))
        with self.assertRaises(api.PermissionDenied):
            api.get_repos(-1)

    def test_invalid_create_repo(self):
        """Create a repository with empty name and description"""
        with self.assertRaises(IntegrityError) as ex:
            api.create_repo(None, "description", self.user.id)
        self.assertIn("name", ex.exception.args[0])

        with self.assertRaises(IntegrityError) as ex:
            api.create_repo("name", None, self.user.id)
        self.assertIn("description", ex.exception.args[0])


def course_count():
    """
    Return number of courses in the database.
    """
    return Course.objects.count()


class TestStaticAsset(LoreTestCase):
    """
    Verify the Python API for static assets.
    """
    def test_create_static_asset(self):
        """
        Validate that we can create assets.
        """
        basename = 'blah.txt'
        file_contents = b'hello\n'
        with tempfile.TemporaryFile() as temp:
            temp.write(file_contents)
            test_file = File(temp, name=basename)
            asset = api.create_static_asset(self.course.id, test_file)
            self.addCleanup(default_storage.delete, asset.asset)
            self.assertFalse(test_file.closed)
            self.assertEqual(asset.course, self.course)
            self.assertEqual(
                static_asset_basepath(asset, basename),
                asset.asset.name
            )

            # Close file and assert that exception is raised.
            test_file.close()
            test_file.name = 'new_name'
            with self.assertRaises(ValueError):
                asset = api.create_static_asset(self.course.id, test_file)
        self.assertEqual(file_contents, asset.asset.read())


class TestDescriptionPath(LoreTestCase):
    """
    Tests the Python API for the description paths
    """
    def test_join_description_path(self):
        """Test for join_description_path"""
        self.assertEqual(
            api.join_description_paths(''),
            ''
        )
        self.assertEqual(
            api.join_description_paths('', 'foo'),
            'foo'
        )
        self.assertEqual(
            api.join_description_paths('foo', ''),
            'foo'
        )
        self.assertEqual(
            api.join_description_paths('foo', '', 'bar'),
            'foo / bar'
        )
        self.assertEqual(
            api.join_description_paths('foo', 'bar', 'b az'),
            'foo / bar / b az'
        )

    def test_update_description_path(self):
        """Tests for update_description_path"""
        # after created a resource without parent has the description path
        # equal to the title
        self.assertIsNone(self.resource.parent)
        self.assertEqual(
            self.resource.title,
            self.resource.description_path
        )
        # changing the title does not update the description path automatically
        self.resource.title = '123 xyz'
        self.resource.save()
        self.assertNotEqual(
            self.resource.title,
            self.resource.description_path
        )
        # update the description path
        api.update_description_path(self.resource)
        self.assertEqual(
            self.resource.title,
            self.resource.description_path
        )
        # create a child resource
        child_res = self.create_resource(
            parent=self.resource
        )
        # the description path is the combination of the child resource title
        # and the parent description path
        self.assertEqual(
            child_res.description_path,
            api.join_description_paths(
                self.resource.description_path,
                child_res.title
            )
        )
        # change both resources title
        self.resource.title = '1234 xyza'
        self.resource.save()
        child_res.title = 'foo 1234'
        child_res.save()
        # note: child_res.parent and self.resource are 2 different instances
        # of the same record, but they need to be refreshed separately
        # after a change made to one of them
        child_res.parent.refresh_from_db()
        # update the description path of the child
        # will not update the parent's one
        api.update_description_path(child_res)
        self.assertNotEqual(
            self.resource.title,
            self.resource.description_path
        )
        self.assertEqual(
            child_res.description_path,
            api.join_description_paths(
                self.resource.description_path,
                child_res.title
            )
        )
        # but the parent's update can be forced
        api.update_description_path(child_res, force_parent_update=True)
        self.resource.refresh_from_db()
        self.assertEqual(
            self.resource.title,
            self.resource.description_path
        )
        self.assertEqual(
            child_res.description_path,
            api.join_description_paths(
                self.resource.description_path,
                child_res.title
            )
        )
        # removing the description path of the parent
        self.resource.description_path = ''
        self.resource.title = '999 new title'
        self.resource.save()
        child_res.parent.refresh_from_db()
        # the update of the child will update the parent without forcing it
        api.update_description_path(child_res)
        self.resource.refresh_from_db()
        self.assertEqual(
            self.resource.title,
            self.resource.description_path
        )

    def test_update_description_path_command(self):
        """
        test the update_description_paths via manage.py
        """
        # pylint: disable=invalid-name, no-self-use
        with patch.object(api, 'update_description_path') as mock_method:
            mock_method.return_value = None
            call_command('update_description_paths')
            mock_method.assert_called_with(self.resource)
