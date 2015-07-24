"""
Functions for communicating with the xanalytics API.
"""
import logging
import os
from tempfile import mkstemp

from django.conf import settings
import requests


log = logging.getLogger(__name__)


def send_request(url, course_id):
    """
    Send initial request to xanalytics API.
    Args:
        url (string): URL of xanalytics API
        course_id (int): Course primary key.
    Returns:
        token (unicode): Job token from xanalytics.
    """
    return requests.post(url=url, data={"course_id": course_id}).json()


def get_result(url, token):
    """
    Get result from xanalytics for token.
    Args:
        token (unicode): Token from xanalytics job.
    Returns:
        data (dict): Dictionary from JSON object provided by xanalytics.
    """
    return requests.post(url=url, data={"token": token}).json()
