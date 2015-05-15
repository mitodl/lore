"""
Tests for LORE imports.
"""

from unittest import TestCase
from os.path import abspath, dirname, exists, join
from os import mkdir

import requests
from django.contrib.auth.models import User

from importer.api import import_course_from_file

# TODO: Also test this course:
# https://github.com/pmitros/edX-Insider/archive/master.zip
def get_course_zip():
    """
    Get the path to the demo course.
    """
    url = "https://github.com/edx/edx-demo-course/archive/master.zip"
    path = join(abspath(dirname(__file__)), "testdata")
    filename = join(path, "edx-demo-course-master.zip")
    if not exists(path):
        mkdir(path)
    if not exists(filename):
        download_file(url, filename)
    return filename

def download_file(url, path):
    """
    Download a file via HTTP and store it locally.
    """
    result = requests.get(url)
    assert result.status_code == 200
    with open(path, "wb") as raw:
        for chunk in result.iter_content(1024**2):
            raw.write(chunk)

class TestImportDemo(TestCase):
    """
    Test import functionality on an actual course. These tests should
    be expanded as needed to test regressions and handle valid but
    non-standard courses.
    """
    def setUp(self):
        """
        Make sure we have a local copy of the edX Demo Course
        for testing.
        """
        super(TestImportDemo, self).setUp()
        self.user, _ = User.objects.get_or_create(username="test")
        self.course_zip = get_course_zip()

    def test_import_demo(self):
        """
        Simplest possible test.
        """
        import_course_from_file(self.course_zip, self.user.id)
