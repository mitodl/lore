"""
Tests for LORE imports.
"""

# standard library
from unittest import TestCase
from os.path import abspath, dirname, exists, join
from os import mkdir

# PyPi
import requests

# local
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
    Test import functionality.
    """
    def setUp(self):
        """
        Make sure we have a local copy of the edX Demo Course
        for testing.
        """
        self.course_zip = get_course_zip()

    def test_read(self):
        """
        Try opening the path and creating an xbundle.
        """
        print import_course_from_file(self.course_zip)
