"""
Tests for tasks API.
"""

from __future__ import unicode_literals
from tempfile import mkdtemp
from shutil import rmtree
import tarfile
import os
import json
import mock

from django.utils.text import slugify
from django.test import override_settings, Client
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from six import BytesIO
from six.moves import reload_module   # pylint: disable=import-error

import ui.urls
from rest.tests.base import (
    RESTTestCase,
    API_BASE,
    as_json,
)
from rest.tasks import EXPORT_TASK_TYPE
from learningresources.models import LearningResource
from exporter.tests.test_export import assert_resource_directory


class TestTasks(RESTTestCase):
    """Tests for tasks."""

    @override_settings(
        DEFAULT_FILE_STORAGE='storages.backends.overwrite.OverwriteStorage'
    )
    def test_create_export_task(self):
        """Test a basic export."""
        self.import_course_tarball(self.repo)
        resources = LearningResource.objects.filter(
            course__repository__id=self.repo.id).all()
        for resource in resources:
            self.create_learning_resource_export(self.repo.slug, {
                "id": resource.id
            })

        # Skip first one to test that it's excluded from export.
        resource_ids = [r.id for r in resources[1:]]

        # Missing task_info.
        self.create_task(
            {
                "ids": resource_ids,
                "task_type": EXPORT_TASK_TYPE
            },
            expected_status=HTTP_400_BAD_REQUEST
        )

        # Missing repo slug.
        self.create_task(
            {
                "ids": resource_ids,
                "task_type": EXPORT_TASK_TYPE,
                "task_info": {}
            },
            expected_status=HTTP_400_BAD_REQUEST
        )

        # Missing ids.
        self.create_task(
            {
                "task_type": EXPORT_TASK_TYPE,
                "task_info": {
                    "repo_slug": self.repo.slug,
                },
            },
            expected_status=HTTP_400_BAD_REQUEST
        )

        # Missing task_type.
        self.create_task(
            {
                "ids": resource_ids,
                "task_info": {
                    "repo_slug": self.repo.slug,
                },
            },
            expected_status=HTTP_400_BAD_REQUEST
        )

        # Invalid task type.
        self.create_task(
            {
                "ids": resource_ids,
                "task_type": "missing",
                "task_info": {
                    "repo_slug": self.repo.slug,
                },
            },
            expected_status=HTTP_400_BAD_REQUEST
        )

        # Invalid repo.
        self.create_task(
            {
                "ids": resource_ids,
                "task_type": EXPORT_TASK_TYPE,
                "task_info": {
                    "repo_slug": "missing",
                },
            },
            expected_status=HTTP_404_NOT_FOUND
        )

        # User doesn't own repo.
        client2 = Client()
        client2.login(
            username=self.user_norepo.username,
            password=self.PASSWORD
        )
        resp = client2.post(
            "{base}tasks/".format(base=API_BASE),
            json.dumps({
                "ids": resource_ids,
                "task_type": EXPORT_TASK_TYPE,
                "task_info": {
                    "repo_slug": self.repo.slug
                }
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, HTTP_403_FORBIDDEN)

        # Start export task. Due to CELERY_ALWAYS_EAGER setting this will
        # block until it completes in testing.
        task_id = self.create_task(
            {
                "task_info": {
                    "repo_slug": self.repo.slug,
                    # Skip first one to test that it's excluded from export.
                    "ids": [r.id for r in resources[1:]],
                },
                "task_type": EXPORT_TASK_TYPE
            }
        )['id']

        # Before we move on, confirm that other user can't see these tasks.
        resp = client2.get("{base}tasks/".format(base=API_BASE))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(as_json(resp)['count'], 0)

        result = self.get_tasks()['results'][0]
        self.assertEqual(task_id, result['id'])
        self.assertEqual("success", result['status'])
        self.assertEqual(result['task_type'], EXPORT_TASK_TYPE)
        self.assertTrue(result['result']['url'].startswith(
            "/media/resource_exports/test_exports.tar"))
        # webGLDemo.css shows up twice
        self.assertTrue(result['result']['collision'])

        with self.settings(
            DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage'
        ):
            # change the default file storage to S3
            reload_module(ui.urls)
            # the view is not available any more
            resp = self.client.get(result['result']['url'])
            self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

        # Update for change in file storage.
        reload_module(ui.urls)

        resp = self.client.get(result['result']['url'])
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

    def test_tasks_in_session(self):
        """
        Test that the task list clears after logout.
        """
        self.assertEqual(self.get_tasks()['count'], 0)
        self.create_task(
            {
                "task_info": {
                    "repo_slug": self.repo.slug,
                    # No ids to export, but task should still run.
                    "ids": [],
                },
                "task_type": EXPORT_TASK_TYPE
            }
        )
        self.assertEqual(self.get_tasks()['count'], 1)

        # Since tasks are stored in session currently they are wiped out.
        self.logout()
        self.login(self.user.username)
        self.assertEqual(self.get_tasks()['count'], 0)

    def test_remove_task(self):
        """
        Test that the task is removed from list properly.
        """
        task_id = self.create_task(
            {
                "task_info": {
                    "repo_slug": self.repo.slug,
                    # No ids to export, but task should still run.
                    "ids": [],
                },
                "task_type": EXPORT_TASK_TYPE
            }
        )['id']
        self.assertEqual(self.get_task(task_id)['status'], 'success')

        # Other users can't stop tasks they don't own.
        client2 = Client()
        client2.login(
            username=self.user_norepo.username,
            password=self.PASSWORD
        )
        resp = client2.delete("{base}tasks/{task_id}/".format(
            base=API_BASE,
            task_id=task_id
        ))
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

        self.delete_task(task_id)
        self.get_task(task_id, expected_status=HTTP_404_NOT_FOUND)
        self.assertEqual(self.get_tasks()['count'], 0)

    @override_settings(
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=False
    )
    def test_failure(self):
        """
        Test that the task exception text is returned in the result.
        """

        with mock.patch('exporter.tasks.export_resources_to_tarball') as imp:
            imp.side_effect = Exception("Failure")
            task_id = self.create_task(
                {
                    "task_info": {
                        "repo_slug": self.repo.slug,
                        # No ids to export, but task should still run.
                        "ids": [],
                    },
                    "task_type": EXPORT_TASK_TYPE
                }
            )['id']
            result = self.get_task(task_id)
            self.assertEqual(result['status'], 'failure')
            self.assertEqual(result['result'], {'error': 'Failure'})

    @override_settings(
        DEFAULT_FILE_STORAGE='storages.backends.overwrite.OverwriteStorage'
    )
    def test_old_export_tasks_api(self):
        """
        Test deprecated export tasks API.
        """
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

        # Test single task API.
        self.assertEqual(
            self.get_learning_resource_export_task(self.repo.slug, task_id),
            result
        )

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
