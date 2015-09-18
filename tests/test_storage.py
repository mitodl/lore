"""
Tests for django storage
"""
from __future__ import unicode_literals

import os
from shutil import rmtree
from tempfile import mkdtemp

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test.testcases import TestCase


class TestStorage(TestCase):
    """
    Tests for Django storage
    """

    def test_local_storage(self):
        """
        Tests for local storage
        It has to be OverwriteStorage to avoid problems with static assets
        having the same name
        """

        # default setting
        self.assertEqual(
            settings.DEFAULT_FILE_STORAGE,
            'storages.backends.overwrite.OverwriteStorage'
        )

        temp_dir_path = mkdtemp()
        self.addCleanup(rmtree, temp_dir_path)

        path = os.path.join(temp_dir_path, 'temp_file.txt')

        # create the first file
        default_storage.save(path, ContentFile('nonsense content'))
        # create another with the same name
        content = 'nonsense content 2'
        default_storage.save(path, ContentFile(content))

        # there is only one file in the directory
        self.assertEqual(len(os.listdir(temp_dir_path)), 1)

        with open(path) as fhand:
            content_read = fhand.read()
        self.assertEqual(content, content_read)
