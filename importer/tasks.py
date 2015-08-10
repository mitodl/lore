"""
Celery tasks for import module.
"""
from __future__ import unicode_literals

import json
import logging

from django.conf import settings
import requests

from lore.celery import async
from learningresources.api import update_xanalytics
from xanalytics import send_request, get_result

log = logging.getLogger(__name__)

RETRY_LIMIT = 10


@async.task
def import_file(path, repo_id, user_id):
    """Asynchronously import a course."""
    from importer.api import import_course_from_file
    import_course_from_file(path, repo_id, user_id)


@async.task
def populate_xanalytics_fields(course_id):
    """
    Initiate request to xanalytics API to get stats for a course,
    then trigger async job to retrieve results when they become available.
    Args:
        course_id (int): primary key of a Course
    """
    if settings.XANALYTICS_URL != "":
        token = send_request(settings.XANALYTICS_URL + "/create", course_id)
        check_for_results.apply_async(
            kwargs={"token": token, "wait": 5, "attempt": 1}, countdown=5)


@async.task
def check_for_results(token, wait, attempt):
    """
    Check for xanalytics results for a course.
    Args:
        token (string): Token received from xanalytics server.
        wait (int): Seconds to wait before repository.
        attempt (int): Attempt number, so we don't try forever.
    """
    resp = get_result(settings.XANALYTICS_URL + "/status", token)
    if resp["status"] == "still busy" and attempt < RETRY_LIMIT:
        attempt += 1
        wait *= 2
        check_for_results.apply_async(
            kwargs={"token": token, "wait": wait, "attempt": attempt},
            countdown=wait,
        )
    if resp["status"] == "complete":
        content = requests.get(resp["url"]).content
        try:
            data = json.loads(content)
            update_xanalytics(data)
        except (ValueError, TypeError):
            log.error("Unable to parse xanalytics response: %s", content)
