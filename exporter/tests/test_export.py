"""
Tests for export
"""

from __future__ import unicode_literals
from tempfile import mkdtemp
from shutil import rmtree
import os

from archive import Archive
from django.core.files.storage import default_storage

from learningresources.tests.base import LoreTestCase
from learningresources.models import (
    LearningResource,
    LearningResourceType,
)
from learningresources.api import update_description_path
from exporter.api import (
    export_resources_to_directory,
    export_resources_to_tarball,
)
from exporter.tasks import export_resources
from learningresources.api import create_resource
from importer.tasks import import_file


class TestExport(LoreTestCase):
    """
    Tests for export
    """

    def setUp(self):
        super(TestExport, self).setUp()

        # Add some LearningResources on top of the default to make things
        # interesting.
        tarball_file = self.get_course_single_tarball()
        import_file(
            tarball_file, self.repo.id, self.user.id)

        # Add a resource with a '/' in the title and too many characters.
        resource = create_resource(
            course=self.repo.course_set.first(),
            resource_type=LearningResourceType.objects.first().name,
            title="//x"*300,
            content_xml="",
            mpath="",
            url_name=None,
            parent=None,
            dpath=''
        )
        update_description_path(resource)

    def assert_resource_directory(self, resources, tempdir):
        """Assert that files are present with correct content."""
        def sanitize(title):
            """Sanitize title for use in filename."""
            # Limit filename to 200 characters since limit is 256
            # and we have a number and extension too.
            return title.replace("/", "_")[:200]

        def make_name(resource):
            """Format expected filename."""
            return "{id}_{title}.xml".format(
                id=resource.id,
                title=sanitize(resource.title),
            )

        for resource in resources:
            abs_path = os.path.join(tempdir, make_name(resource))
            self.assertTrue(os.path.exists(abs_path))
            with open(abs_path) as f:
                self.assertEqual(f.read(), resource.content_xml)

    def test_export_resources_to_directory(self):
        """Test exporting learning resources to directory."""
        resources = LearningResource.objects.all()

        tempdir = mkdtemp()
        try:
            export_resources_to_directory(resources, tempdir)
            self.assert_resource_directory(resources, tempdir)
        finally:
            rmtree(tempdir)

    def test_export_resources_to_tarball(self):
        """Test exporting learning resources to tarball."""
        resources = LearningResource.objects.all()

        path = export_resources_to_tarball(resources, self.user.username)
        tempdir = mkdtemp()

        # HACK: Have to patch in "seekable" attribute for python3 and tar
        # See: https://code.djangoproject.com/ticket/24963#ticket. Remove
        # when updating to Django 1.9
        def seekable():
            """Hacked seekable for django storage to work in python3."""
            return True
        try:
            resource_archive = default_storage.open(path)
            resource_archive.seekable = seekable
            Archive(resource_archive, ext='.tar.gz').extract(
                to_path=tempdir, method='safe'
            )
            self.assert_resource_directory(resources, tempdir)
        finally:
            rmtree(tempdir)
            default_storage.delete(path)

    def test_export_task(self):
        """Test exporting resources task."""
        resources = LearningResource.objects.all()

        path = export_resources.delay(resources, self.user.username).get()
        tempdir = mkdtemp()

        # HACK: Have to patch in "seekable" attribute for python3 and tar
        # See: https://code.djangoproject.com/ticket/24963#ticket. Remove
        # when updating to Django 1.9
        def seekable():
            """Hacked seekable for django storage to work in python3."""
            return True
        try:
            resource_archive = default_storage.open(path)
            resource_archive.seekable = seekable
            Archive(resource_archive, ext='.tar.gz').extract(
                to_path=tempdir, method='safe'
            )
            self.assert_resource_directory(resources, tempdir)
        finally:
            rmtree(tempdir)
            default_storage.delete(path)
