"""
Exporter tasks for LORE
"""

from __future__ import unicode_literals

from django.core.files.storage import default_storage

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
        dict:
            name is path of tarball.
            url is URL of tarball using django-storage.
            collision is True if a static asset collision was detected.
    """
    name, collision = export_resources_to_tarball(learning_resources, username)
    return {
        "name": name,
        "url": default_storage.url(name),
        "collision": collision
    }
