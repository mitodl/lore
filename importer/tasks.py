"""
Celery tasks for import module.
"""
from __future__ import unicode_literals

from lore.celery import async
from importer.api import import_course_from_file


@async.task
def import_file(path, repo_id, user_id):
    """Asynchronously import a course."""
    import_course_from_file(path, repo_id, user_id)
