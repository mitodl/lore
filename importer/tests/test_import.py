"""
Tests for LORE imports.
"""

from __future__ import unicode_literals

from collections import namedtuple
import os
from shutil import rmtree
from tempfile import mkstemp, mkdtemp
import zipfile
import logging

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import mock

from importer.api import (
    import_course_from_file,
    import_course_from_path,
    import_static_assets,
)
from importer.tasks import import_file
from learningresources.api import get_resources
from learningresources.models import (
    Course, StaticAsset, static_asset_basepath, LearningResource,
)
from learningresources.tests.base import LoreTestCase

log = logging.getLogger(__name__)


class TestImportToy(LoreTestCase):
    """
    Test import functionality on an actual course. These tests should
    be expanded as needed to test regressions and handle valid but
    non-standard courses.
    """
    def setUp(self):
        """
        Return location of the local copy of the "simple" course for testing.
        """
        super(TestImportToy, self).setUp()
        self.course_zip = self.get_course_zip()
        self.bad_file = default_storage.save('bad_file', ContentFile(''))
        self.addCleanup(default_storage.delete, self.bad_file)

        # Valid zip file, wrong stuff in it.
        handle, bad_zip = mkstemp(suffix=".zip")
        os.close(handle)
        self.addCleanup(os.remove, bad_zip)
        archive = zipfile.ZipFile(
            bad_zip, "w", compression=zipfile.ZIP_DEFLATED)
        archive.close()
        self.incompatible = default_storage.save(
            'bad_zip.zip', open(bad_zip, 'rb')
        )
        self.addCleanup(default_storage.delete, self.incompatible)

    def test_import_toy(self):
        """
        Simplest possible test.
        """
        resource_count = get_resources(self.repo.id).count()
        course_count = Course.objects.count()
        import_course_from_file(self.course_zip, self.repo.id, self.user.id)
        self.assertEqual(
            get_resources(self.repo.id).count(),
            resource_count + self.toy_resource_count)
        self.assertEqual(
            Course.objects.count(),
            course_count + 1,
        )

    def test_import_multiple(self):
        """
        Simplest possible test.
        """
        original_count = Course.objects.count()
        import_course_from_file(
            self.get_course_multiple_zip(), self.repo.id, self.user.id)
        self.assertEqual(
            Course.objects.count(),
            original_count + 2,
        )

    def test_invalid_file(self):
        """Invalid zip file"""
        with self.assertRaises(ValueError) as ex:
            import_course_from_file(self.bad_file, self.repo.id, self.user.id)
        self.assertTrue(
            'Invalid OLX archive, unable to extract.' in ex.exception.args)
        self.assertFalse(os.path.exists(self.bad_file))

    def test_incompatible_file(self):
        """incompatible zip file (missing course structure)"""
        with self.assertRaises(ValueError) as ex:
            import_course_from_file(
                self.incompatible, self.repo.id, self.user.id)
        self.assertTrue(
            'Invalid OLX archive, no courses found.' in ex.exception.args)

    def test_import_single(self):
        """
        Single course (course.xml in root of archive).
        """
        original_count = Course.objects.count()
        tarball_file = self.get_course_single_tarball()
        import_course_from_file(
            tarball_file, self.repo.id, self.user.id)
        self.assertEqual(
            Course.objects.count(),
            original_count + 1,
        )
        self.assertFalse(os.path.exists(tarball_file))

    def test_import_task(self):
        """
        Copy of test_import_single that just exercises tasks.py.
        """
        original_count = Course.objects.count()
        import_file(
            self.get_course_single_tarball(), self.repo.id, self.user.id)
        self.assertEqual(
            Course.objects.count(),
            original_count + 1,
        )

    @staticmethod
    def test_import_course_from_path():
        """
        Validate parameters and returns for ``course_from_path``.
        """
        test_path = '/tmp/foo'
        test_repo_id = 2
        test_user_id = 42
        with mock.patch('importer.api.import_course') as mock_import:
            with mock.patch(
                'importer.api.import_static_assets'
            ):
                with mock.patch('importer.api.XBundle') as mock_bundle:
                    mock_import.return_value = True
                    import_course_from_path(
                        test_path, test_repo_id, test_user_id
                    )
                    mock_import.assert_called_with(
                        mock_bundle(), test_repo_id,
                        test_user_id, os.path.join(test_path, "static"),
                    )

    def test_import_static_assets(self):
        """
        Verify walking a folder of assets and verifying they get added
        """
        temp_dir_path = mkdtemp()
        self.addCleanup(rmtree, temp_dir_path)
        basename = 'blah.txt'
        file_contents = 'hello\n'
        with open(os.path.join(temp_dir_path, basename), 'w') as temp:
            temp.write(file_contents)
        # All setup, now import
        import_static_assets(self.course, temp_dir_path)
        assets = StaticAsset.objects.filter(course=self.course)
        self.assertEqual(assets.count(), 1)
        asset = assets[0]
        dummy = mock.MagicMock()
        dummy.course = self.course
        self.assertEqual(
            asset.asset.name,
            static_asset_basepath(dummy, basename)
        )
        self.addCleanup(default_storage.delete, asset.asset)

    def test_import_static_recurse(self):
        """
        Verify walking a folder of assets and verifying they get added
        """
        temp_dir_path = mkdtemp()
        self.addCleanup(rmtree, temp_dir_path)
        basename = 'blah.txt'
        file_contents = 'hello\n'
        # Create folder and additional directory to verify recursion.
        subdir_name = 'testdir'
        os.mkdir(os.path.join(temp_dir_path, subdir_name))
        with open(
            os.path.join(temp_dir_path, subdir_name, basename),
            'w'
        ) as temp:
            temp.write(file_contents)

        # All setup, now import
        import_static_assets(self.course, temp_dir_path)
        assets = StaticAsset.objects.filter(course=self.course)
        self.assertEqual(assets.count(), 1)
        asset = assets[0]
        dummy = mock.MagicMock()
        dummy.course = self.course
        self.assertEqual(
            asset.asset.name,
            static_asset_basepath(dummy, os.path.join(subdir_name, basename))
        )
        self.addCleanup(default_storage.delete, asset.asset)

    def test_static_import_integration(self):
        """
        Do integration test to validate course import with static assets.
        """
        original_count = Course.objects.count()
        tarball_file = self.get_course_single_tarball()
        import_file(
            tarball_file, self.repo.id, self.user.id)
        self.assertEqual(
            Course.objects.count(),
            original_count + 1,
        )
        self.assertFalse(os.path.exists(tarball_file))
        course = Course.objects.all().exclude(id=self.course.id)
        self.assertEqual(course.count(), 1)
        assets = StaticAsset.objects.filter(course=course)
        for asset in assets:
            self.addCleanup(default_storage.delete, asset.asset)
        self.assertEqual(assets.count(), self.toy_asset_count)
        for asset in assets:
            base_path = static_asset_basepath(asset, '')
            self.assertIn(
                asset.asset.name.replace(base_path, ''),
                [
                    'test.txt', 'subdir/subtext.txt',
                    'subs_CCxmtcICYNc.srt.sjson',
                    'essays_x250.png', 'webGLDemo.css',
                ]
            )

    def test_parse_static(self):
        """
        Parse the static assets in the sample course
        """
        def get_counts():
            """Returns counts of resources, videos, and assets."""
            counts = namedtuple("counts", "resources videos assets")
            kwargs = {"course__course_number": "toy"}
            resources = LearningResource.objects.filter(**kwargs).count()
            assets = StaticAsset.objects.filter(**kwargs).count()
            kwargs["learning_resource_type__name"] = "video"
            videos = LearningResource.objects.filter(**kwargs).count()
            return counts(resources, videos, assets)

        # There should be nothing.
        counts = get_counts()
        self.assertEqual(counts.resources, 0)
        self.assertEqual(counts.videos, 0)
        self.assertEqual(counts.assets, 0)
        # Import the course.
        import_course_from_file(
            self.get_course_single_tarball(),
            self.repo.id, self.user.id
        )
        # There should be something.
        counts = get_counts()
        self.assertEqual(counts.resources, self.toy_resource_count)
        self.assertEqual(counts.videos, 2)
        self.assertEqual(counts.assets, self.toy_asset_count)

        # There should be a single static asset.
        course = Course.objects.all().order_by("-id")[0]  # latest course
        videos = LearningResource.objects.filter(
            learning_resource_type__name="video",
            course__id=course.id
        )
        self.assertTrue(videos.count() == 2)
        num_assets = sum([
            video.static_assets.count()
            for video in videos
        ])
        # Only one video in the course has subtitles.
        self.assertTrue(num_assets == 1)

        # The course has an HTML block with two static assets; a CSS
        # file and an image.
        htmls = LearningResource.objects.filter(
            course__course_number='toy',
            learning_resource_type__name="html",
            static_assets__id__isnull=False,
        ).distinct()
        self.assertEqual(htmls.count(), 1)
        self.assertEqual(
            sorted([
                asset.asset.name for asset in htmls[0].static_assets.all()]),
            sorted([
                "assets/edX/toy/TT_2012_Fall/essays_x250.png",
                "assets/edX/toy/TT_2012_Fall/webGLDemo.css",
            ])
        )
