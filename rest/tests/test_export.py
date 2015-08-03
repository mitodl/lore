"""
Tests for export
"""

from __future__ import unicode_literals
from tempfile import mkdtemp
from shutil import rmtree
import os
import tarfile

from django.utils.text import slugify
from django.test import override_settings
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from six import BytesIO
from six.moves import reload_module   # pylint: disable=import-error

import ui.urls
from rest.tests.base import (
    RESTTestCase
)


class TestExport(RESTTestCase):
    """Test for export."""

    @override_settings(
        DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
    )
    def test_create_new_task(self):
        """Test a basic export."""
        self.create_learning_resource_export(self.repo.slug, {
            "id": self.resource.id
        })

        task_id = self.create_learning_resource_export_task(
            self.repo.slug)['id']

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
        try:
            fakefile = BytesIO(b"".join(resp.streaming_content))
            with tarfile.open(fileobj=fakefile, mode="r:gz") as tar:
                tar.extractall(path=tempdir)

            self.assertTrue(os.path.isfile(os.path.join(
                tempdir, "{id}_{name}.xml".format(
                    id=self.resource.id,
                    name=slugify(self.resource.title),
                ))))
        finally:
            rmtree(tempdir)
