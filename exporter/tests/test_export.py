"""
Tests for export
"""

from __future__ import unicode_literals
from tempfile import mkdtemp, TemporaryFile
from shutil import rmtree
import os

from archive import Archive
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.text import slugify

from learningresources.tests.base import LoreTestCase
from learningresources.models import (
    LearningResource,
    LearningResourceType,
    STATIC_ASSET_BASEPATH,
)
from learningresources.api import (
    update_description_path,
    create_static_asset,
)
from exporter.api import (
    export_resources_to_directory,
    export_resources_to_tarball,
)
from exporter.tasks import export_resources
from learningresources.api import (
    create_resource,
    create_course,
)
from importer.tasks import import_file


# pylint: disable=too-many-locals
def assert_resource_directory(test_case, resources, tempdir):
    """Assert that files are present with correct content."""
    def make_name(resource):
        """Format expected filename."""
        if resource.url_name is not None:
            return "{id}_{url_name}.xml".format(
                id=resource.id,
                url_name=slugify(resource.url_name)[:200],
            )
        else:
            return "{id}.xml".format(id=resource.id)

    # Key is filename, value is count of filenames encountered.
    asset_map = {}

    # Verify that content XML exists in right place.
    for resource in resources:
        type_name = resource.learning_resource_type.name
        abs_path = os.path.join(tempdir, type_name, make_name(resource))
        test_case.assertTrue(os.path.exists(abs_path))
        with open(abs_path) as f:
            test_case.assertEqual(f.read(), resource.content_xml)

        # Verify static asset placement.
        for static_asset in resource.static_assets.all():
            prefix = STATIC_ASSET_BASEPATH.format(
                org=static_asset.course.org,
                course_number=static_asset.course.course_number,
                run=static_asset.course.run
            )
            static_filename = static_asset.asset.name[len(prefix):]

            if static_filename in asset_map:
                count = asset_map[static_filename]
                asset_map[static_filename] += 1
                base, ext = os.path.splitext(static_filename)

                static_filename = "{base}_{count}{ext}".format(
                    base=base,
                    ext=ext,
                    count=count
                )
            else:
                asset_map[static_filename] = 1

            relative_path = os.path.join("static", static_filename)
            abs_path = os.path.join(tempdir, relative_path)
            test_case.assertTrue(os.path.exists(abs_path))
            with open(abs_path, 'rb') as f:
                test_case.assertEqual(f.read(), static_asset.asset.read())


class TestExport(LoreTestCase):
    """
    Tests for export
    """

    def setUp(self):
        super(TestExport, self).setUp()

        # Add some LearningResources on top of the default to make things
        # interesting.
        tarball_file = self.get_course_single_tarball()
        import_file(tarball_file, self.repo.id, self.user.id)

        # Add a resource with a '/' in the title and too many characters.
        course = self.repo.course_set.first()
        resource = create_resource(
            course=course,
            resource_type=LearningResourceType.objects.first().name,
            title="//x"*300,
            content_xml="",
            mpath="",
            url_name=None,
            parent=None,
            dpath=''
        )
        update_description_path(resource)

        # Add static assets.
        with TemporaryFile() as temp1:
            with TemporaryFile() as temp2:
                temp1.write(b"file1")
                temp2.write(b"file2")
                file1 = File(temp1, name="iamafile1.txt")
                file2 = File(temp2, name="iamafile2.txt")

                asset1 = create_static_asset(course.id, file1)
                resource.static_assets.add(asset1)

                # If url_name is missing we should just use id in filename.
                resource.url_name = None
                resource.save()

                asset2 = create_static_asset(course.id, file2)
                self.resource.static_assets.add(asset2)

    def test_export_resources_to_directory(self):
        """Test exporting learning resources to directory."""

        resources = LearningResource.objects.all()

        tempdir, collision = export_resources_to_directory(resources)
        try:
            self.assertTrue(collision)
            assert_resource_directory(self, resources, tempdir)
        finally:
            rmtree(tempdir)

    def test_export_resources_to_tarball(self):
        """Test exporting learning resources to tarball."""
        resources = LearningResource.objects.all()

        path, collision = export_resources_to_tarball(
            resources, self.user.username)
        tempdir = mkdtemp()

        self.assertTrue(collision)

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
            assert_resource_directory(self, resources, tempdir)
        finally:
            rmtree(tempdir)
            default_storage.delete(path)

    def test_export_task(self):
        """Test exporting resources task."""
        resources = LearningResource.objects.all()

        path, collision = export_resources.delay(
            resources, self.user.username).get()
        tempdir = mkdtemp()

        self.assertTrue(collision)

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
            assert_resource_directory(self, resources, tempdir)
        finally:
            rmtree(tempdir)
            default_storage.delete(path)

    def test_duplicate(self):
        """
        Test that exporting resources with same file path
        is reported and handled correctly.
        """

        with TemporaryFile() as temp1:
            with TemporaryFile() as temp2:
                temp1.write(b"first")
                temp2.write(b"second")

                # Create two static assets with the same name but different
                # paths so no renaming is done on storage side.
                static_filename = "iamafile.txt"
                static_path1 = os.path.join(
                    STATIC_ASSET_BASEPATH.format(
                        org=self.resource.course.org,
                        course_number=self.resource.course.course_number,
                        run=self.resource.course.run,
                    ),
                    static_filename
                )

                file1 = File(temp1, name=static_filename)
                file2 = File(temp2, name=static_filename)

                default_storage.delete(static_path1)
                asset1 = create_static_asset(self.resource.course.id, file1)
                self.resource.static_assets.add(asset1)

                course2 = create_course(
                    "org2", self.repo.id, self.resource.course.course_number,
                    self.resource.course.run, self.user.id
                )
                resource2 = create_resource(
                    course=course2,
                    parent=None,
                    resource_type=self.resource.learning_resource_type.name,
                    title=self.resource.title,
                    dpath="",
                    mpath="",
                    content_xml="",
                    url_name=self.resource.url_name
                )
                static_path2 = os.path.join(
                    STATIC_ASSET_BASEPATH.format(
                        org=course2.org,
                        course_number=course2.course_number,
                        run=course2.run,
                    ),
                    static_filename
                )
                default_storage.delete(static_path2)
                asset2 = create_static_asset(resource2.course.id, file2)
                resource2.static_assets.add(asset2)

                # Export the resources. The second static asset should have
                # the number _1 attached to it.
                try:

                    resources = [self.resource, resource2]
                    tempdir, collision = export_resources_to_directory(
                        resources)
                    try:
                        self.assertTrue(collision)
                        assert_resource_directory(self, resources, tempdir)
                    finally:
                        rmtree(tempdir)
                finally:
                    default_storage.delete(asset1.asset.name)
                    default_storage.delete(asset2.asset.name)
