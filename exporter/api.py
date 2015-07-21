"""
Functions for exporting learning resources
"""

from __future__ import unicode_literals

from tempfile import mkdtemp, mkstemp
import tarfile
import os
from shutil import rmtree

from django.utils.text import slugify
from django.core.files.storage import default_storage
from lore.settings import EXPORT_PATH_PREFIX


def export_resources_to_directory(learning_resources):
    """
    Create files of LearningResource and StaticAsset contents inside directory.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
    Returns:
        unicode: Newly created temp directory with files inside of it.
    """
    def sanitize(title):
        """Sanitize title for use in filename."""
        # Limit filename to 200 characters since limit is 256
        # and we have a number and extension too.
        return slugify(title)[:200]

    tempdir = mkdtemp()
    try:
        for learning_resource in learning_resources:
            filename = "{id}_{title}.xml".format(
                id=learning_resource.id,
                title=sanitize(learning_resource.title),
            )
            with open(os.path.join(tempdir, filename), 'w') as f:
                f.write(learning_resource.content_xml)
    except:
        # Clean up temporary directory since we can't return it anymore.
        rmtree(tempdir)
        raise
    return tempdir


def export_resources_to_tarball(learning_resources, username):
    """
    Create tarball and put LearningResource and StaticAsset contents in it.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
        username (unicode): Name of user
    Returns:
        unicode: path of tarball within django-storage
    """
    handle, tempfilepath = mkstemp()
    os.close(handle)
    try:
        archive = tarfile.open(tempfilepath, mode='w:gz')

        tempdir = export_resources_to_directory(learning_resources)
        try:
            for name in os.listdir(tempdir):
                abs_path = os.path.join(tempdir, name)
                if os.path.isfile(abs_path):
                    archive.add(abs_path, arcname=name)

            archive.close()
            output_path = '{prefix}{username}_exports.tar.gz'.format(
                prefix=EXPORT_PATH_PREFIX,
                username=username
            )

            # Remove any old paths.
            default_storage.delete(output_path)
            return default_storage.save(output_path, open(tempfilepath, 'rb'))
        finally:
            rmtree(tempdir)
    finally:
        os.remove(tempfilepath)
