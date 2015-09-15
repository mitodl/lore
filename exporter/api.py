"""
Functions for exporting learning resources
"""

from __future__ import unicode_literals

import errno
import os
import re
import tarfile
from shutil import rmtree
from tempfile import mkdtemp, mkstemp

from django.utils.text import slugify
from django.core.files.storage import default_storage
from lore.settings import EXPORT_PATH_PREFIX
from learningresources.models import STATIC_ASSET_BASEPATH


def _find_unused_path(path):
    """Iterate through filenames until we get to one that isn't taken."""
    base, ext = os.path.splitext(path)

    collision = False
    i = 1
    while os.path.exists(path):
        collision = True
        path = "{base}_{i}{ext}".format(
            base=base,
            ext=ext,
            i=i
        )
        i += 1

    return path, collision


# pylint: disable=too-many-locals
def export_resources_to_directory(learning_resources):
    """
    Create files of LearningResource and StaticAsset contents inside directory.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
    Returns:
        (unicode, bool):
            First item is newly created temp directory with files inside of it.
            Second item is True if a static asset collision was detected.
    """
    def sanitize(url_name):
        """Sanitize title for use in filename."""
        # Limit filename to 200 characters since limit is 256
        # and we have a number and extension too.
        return slugify(url_name)[:200]

    tempdir = mkdtemp()
    collision = False
    type_dirs_created = set()
    try:
        os.mkdir(os.path.join(tempdir, "static"))
        for learning_resource in learning_resources:
            if learning_resource.url_name is not None:
                filename = "{id}_{url_name}.xml".format(
                    id=learning_resource.id,
                    url_name=sanitize(learning_resource.url_name),
                )
            else:
                filename = "{id}.xml".format(id=learning_resource.id)

            type_name = learning_resource.learning_resource_type.name
            if type_name not in type_dirs_created:
                os.mkdir(os.path.join(tempdir, type_name))
                type_dirs_created.add(type_name)
            with open(os.path.join(tempdir, type_name, filename), 'w') as f:
                f.write(learning_resource.content_xml)

            # Output to static directory.
            for static_asset in learning_resource.static_assets.all():
                prefix = STATIC_ASSET_BASEPATH.format(
                    org=static_asset.course.org,
                    course_number=static_asset.course.course_number,
                    run=static_asset.course.run,
                )
                asset_path = static_asset.asset.name
                if asset_path.startswith(prefix):
                    asset_path = asset_path[len(prefix):]

                static_path = os.path.join(tempdir, "static", asset_path)
                static_path, found_collision = _find_unused_path(static_path)
                if found_collision:
                    collision = found_collision

                path, _ = os.path.split(static_path)
                try:
                    os.makedirs(path)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(path):
                        pass
                    else:
                        raise
                with open(static_path, 'wb') as outfile:
                    outfile.write(static_asset.asset.read())

        # If we never put anything in static, remove it.
        if not os.listdir(os.path.join(tempdir, "static")):
            rmtree(os.path.join(tempdir, "static"))
    except:
        # Clean up temporary directory since we can't return it anymore.
        rmtree(tempdir)
        raise
    return tempdir, collision


def export_resources_to_tarball(learning_resources, username):
    """
    Create tarball and put LearningResource and StaticAsset contents in it.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
        username (unicode): Name of user
    Returns:
        (unicode, bool):
            First item is path of tarball within django-storage.
            Second item is whether a static asset collision was detected.
    """
    handle, tempfilepath = mkstemp()
    os.close(handle)
    try:
        oldcwd = os.getcwd()
        tempdir, collision = export_resources_to_directory(learning_resources)
        try:
            os.chdir(tempdir)
            archive = tarfile.open(tempfilepath, mode='w:gz')

            for root, _, files in os.walk("."):
                for name in files:
                    abs_path = os.path.join(root, name)
                    abs_path = re.sub(r'^\./', '', abs_path)
                    archive.add(abs_path)

            archive.close()
            output_path = '{prefix}{username}_exports.tar.gz'.format(
                prefix=EXPORT_PATH_PREFIX,
                username=username
            )

            # Remove any old paths.
            default_storage.delete(output_path)
            return (
                default_storage.save(output_path, open(tempfilepath, 'rb')),
                collision
            )
        finally:
            os.chdir(oldcwd)
            rmtree(tempdir)
    finally:
        os.remove(tempfilepath)
