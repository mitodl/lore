"""
Tests for learningresources models
"""
from __future__ import unicode_literals

import os
import random
import string
from shutil import rmtree
from tempfile import mkdtemp

from django.conf import settings
from django.core.files import File
from mock import MagicMock

from .base import LoreTestCase
from learningresources.models import (
    FILE_PATH_MAX_LENGTH,
    LearningResource,
    LearningResourceType,
    Repository,
    static_asset_basepath,
    StaticAsset,
    FilePathLengthException,
    get_preview_url,
)


def get_random_string(length):
    """Helper function to generate strings with random characters"""
    return ''.join(
        random.SystemRandom(0).choice(
            string.ascii_letters + string.digits
        ) for _ in range(length)
    )


def get_random_path(length):
    """Helper function to generate strings with random characters"""
    if length < 256:
        return get_random_string(length)
    file_path = ''
    while len(file_path) < length:
        if length - len(file_path) > 255:
            file_path += get_random_string(255)
            file_path += os.sep
        else:
            file_path += get_random_string(length - len(file_path))
    return file_path


def create_dumb_file(temp_dir_path, basename_length):
    """helper function to create test files"""
    random_path = get_random_path(basename_length)
    # saving current directory
    cur_dir = os.getcwd()
    # going to the base of the directory that should be already there
    os.chdir(temp_dir_path)
    # create the chain of folders
    splitted_path = random_path.split(os.sep)
    while len(splitted_path) > 1:
        dirname = splitted_path.pop(0)
        os.mkdir(dirname)
        os.chdir(dirname)
    # finally create the file
    file_contents = 'hello\n'
    with open(splitted_path[0], 'w') as temp:
        temp.write(file_contents)
    os.chdir(cur_dir)
    return os.path.join(temp_dir_path, random_path)


class MockAsset(object):
    """Mock Asset class"""
    def __init__(self, course):
        self.course = course


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

    def test_static_asset_basepath(self):
        """Verify we are setting the path we expect"""
        filename = 'asdf/asdf.txt'
        asset = MagicMock()
        asset.course.org = 'hi'
        asset.course.course_number = '1'
        asset.course.run = 'runnow'
        path = static_asset_basepath(asset, filename)
        self.assertEqual(
            path,
            'assets/hi/1/runnow/asdf/asdf.txt'
        )

    def test_static_asset_filename_length(self):
        """
        Tests that user can use django FileField long up to
        FILE_PATH_MAX_LENGTH characters
        """
        temp_dir_path = mkdtemp()
        self.addCleanup(rmtree, temp_dir_path)

        # test with small file name
        file_path = create_dumb_file(temp_dir_path, 10)
        with open(file_path) as file_handle:
            StaticAsset.objects.create(
                course=self.course,
                asset=File(file_handle)
            )
        # test with file name of exactly the max length
        base_path = static_asset_basepath(MockAsset(self.course), '')
        file_path = create_dumb_file(
            temp_dir_path,
            (
                # max file size
                FILE_PATH_MAX_LENGTH -
                # minus the length of the base path of the Django storage and
                # the base path of the file location temporary dir
                len(os.path.join(base_path, temp_dir_path)) -
                # minus 1 for the extra "/" to joint the paths
                1
            )
        )
        with open(file_path) as file_handle:
            StaticAsset.objects.create(
                course=self.course,
                asset=File(file_handle)
            )
        # test with file name of more the max length
        file_path = create_dumb_file(temp_dir_path, FILE_PATH_MAX_LENGTH+1)
        with open(file_path) as file_handle:
            self.assertRaises(
                FilePathLengthException,
                lambda: StaticAsset.objects.create(
                    course=self.course,
                    asset=File(file_handle)
                )
            )

    def test_preview_url(self):
        """
        Test get_preview_url function. It returns different results depending
        upon whether property url_name is None.
        """
        base_url = "{0}courses/org/".format(settings.LORE_PREVIEW_BASE_URL)
        resource = LearningResource()

        kwargs = {
            'resource': resource,
            'org': "org",
            'course_number': 'babelfish',
            'run': 'gazelle',
        }

        tests = (
            (None, '{0}babelfish/gazelle/courseware'.format(base_url)),
            ("WNYX", '{0}babelfish/gazelle/jump_to_id/WNYX'.format(base_url))
        )

        for url_name, wanted in tests:
            resource.url_name = url_name
            url = get_preview_url(**kwargs)
            self.assertEqual(url, wanted)
