"""
Functions for exporting learning resources
"""

from __future__ import unicode_literals

import os
import re
import tarfile
from shutil import rmtree
from tempfile import mkdtemp, mkstemp

from django.utils.text import slugify
from django.core.files.storage import default_storage
from lore.settings import EXPORT_PATH_PREFIX


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

            for static_asset in learning_resource.static_assets.all():
                # Output to static directory.

                def static_file_path(name):
                    """Convenience function for making a static path."""
                    return os.path.join(tempdir, "static", name)

                static_filename = os.path.basename(static_asset.asset.name)
                base, ext = os.path.splitext(static_filename)

                i = 1
                while os.path.exists(static_file_path(static_filename)):
                    collision = True
                    static_filename = "{base}_{i}{ext}".format(
                        base=base,
                        ext=ext,
                        i=i
                    )
                    i += 1

                with open(static_file_path(static_filename), 'wb') as outfile:
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
