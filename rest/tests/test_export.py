"""
Tests for export
"""

from __future__ import unicode_literals
from tempfile import mkdtemp
from shutil import rmtree
import tarfile
import os

from django.utils.text import slugify
from django.test import override_settings
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from six import BytesIO
from six.moves import reload_module   # pylint: disable=import-error

import ui.urls
from rest.tests.base import (
    RESTTestCase
)
from learningresources.models import LearningResource
from exporter.tests.test_export import assert_resource_directory


class TestExport(RESTTestCase):
    """Test for export."""

    @override_settings(
        DEFAULT_FILE_STORAGE='storages.backends.overwrite.OverwriteStorage'
    )
    def test_create_new_task(self):
        """Test a basic export."""
        self.import_course_tarball(self.repo)
        resources = LearningResource.objects.filter(
            course__repository__id=self.repo.id).all()
        for resource in resources:
            self.create_learning_resource_export(self.repo.slug, {
                "id": resource.id
            })

        # Skip first one to test that it's excluded from export.
        task_id = self.create_learning_resource_export_task(
            self.repo.slug,
            {"ids": [r.id for r in resources[1:]]}
        )['id']

        result = self.get_learning_resource_export_tasks(
            self.repo.slug)['results'][0]
        self.assertEqual(task_id, result['id'])
        self.assertEqual("success", result['status'])
        self.assertTrue(result['url'].startswith(
            "/media/resource_exports/test_exports.tar"))

        with self.settings(
            DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage'
        ):
            # change the default file storage to S3
            reload_module(ui.urls)
            # the view is not available any more
            resp = self.client.get(result['url'])
            self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

        # Update for change in file storage.
        reload_module(ui.urls)

        resp = self.client.get(result['url'])
        self.assertEqual(HTTP_200_OK, resp.status_code)

        tempdir = mkdtemp()

        def make_path(resource):
            """Create a path that should exist for a resource."""
            type_name = resource.learning_resource_type.name
            return os.path.join(
                tempdir, type_name, "{id}_{url_name}.xml".format(
                    id=resource.id,
                    url_name=slugify(resource.url_name)[:200],
                )
            )
        try:
            fakefile = BytesIO(b"".join(resp.streaming_content))
            with tarfile.open(fileobj=fakefile, mode="r:gz") as tar:
                tar.extractall(path=tempdir)

            self.assertFalse(os.path.isfile(make_path(resources[0])))
            assert_resource_directory(self, resources[1:], tempdir)

        finally:
            rmtree(tempdir)
