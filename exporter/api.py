"""
Functions for exporting learning resources
"""

from __future__ import unicode_literals

from tempfile import mkdtemp, mkstemp
import tarfile
import os
from shutil import rmtree

from django.core.files.storage import default_storage
from lore.settings import EXPORT_PATH_PREFIX


def export_resources_to_directory(learning_resources, tempdir):
    """
    Create XML files of learning resource contents inside directory.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
    """
    def sanitize(title):
        """Sanitize title for use in filename."""
        # Limit filename to 200 characters since limit is 256
        # and we have a number and extension too.
        return title.replace("/", "_")[:200]

    for learning_resource in learning_resources:
        filename = "{id}_{title}.xml".format(
            id=learning_resource.id,
            title=sanitize(learning_resource.title),
        )
        with open(os.path.join(tempdir, filename), 'w') as f:
            f.write(learning_resource.content_xml)


def export_resources_to_tarball(learning_resources, username):
    """
    Create tarball and put learning resource contents in it as XML files.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
        username (unicode): Name of user
    Returns:
        unicode: path of tarball within django-storage
    """
    tempdir = mkdtemp()
    handle, tempfilepath = mkstemp()
    os.close(handle)
    try:
        archive = tarfile.open(tempfilepath, mode='w:gz')

        export_resources_to_directory(learning_resources, tempdir)

        for name in os.listdir(tempdir):
            abs_path = os.path.join(tempdir, name)
            if os.path.isfile(abs_path):
                archive.add(abs_path, arcname=name)

        archive.close()
        output_path = '{prefix}{username}_exports.tar.gz'.format(
            prefix=EXPORT_PATH_PREFIX,
            username=username
        )
        return default_storage.save(output_path, open(tempfilepath, 'rb'))
    finally:
        os.unlink(tempfilepath)
        rmtree(tempdir)
