"""
Exporter tasks for LORE
"""

from __future__ import unicode_literals

from lore.celery import async
from exporter.api import export_resources_to_tarball


@async.task
def export_resources(learning_resources, username):
    """
    Asynchronously export learning resources as tarball.

    Args:
        learning_resources (list of learningresources.models.LearningResource):
            LearningResources to export in tarball
        username (unicode): Name of user
    Returns:
        (unicode, bool):
            First item is newly created temp directory with files inside of it.
            Second item is True if a static asset collision was detected.
    """
    return export_resources_to_tarball(learning_resources, username)
