"""
Functions for communicating with the xanalytics API.
"""
import logging
import os
from tempfile import mkstemp

from django.conf import settings
from requests.exceptions import ConnectionError as RequestsConnectionError
import requests


log = logging.getLogger(__name__)


def _call(url, data):
    """
    Make call via requests, trapping common errors.
    Args:
        url (unicode): URL
        data (dict): POST parameters
    Returns:
        result (dict): Results read as JSON
    """
    try:
        resp = requests.post(url=url, data=data)
        try:
            return resp.json()
        except ValueError as ex:
            log.error("Bad JSON returned: %s", ex.args)
    except RequestsConnectionError as ex:
        log.error("Unable to connect to xanalytics server: %s", ex.args)

    # Fallback in case things fail.
    return {}


def send_request(url, course_id):
    """
    Send initial request to xanalytics API.
    Args:
        url (string): URL of xanalytics API
        course_id (int): Course primary key.
    Returns:
        token (unicode): Job token from xanalytics.
    """
    return _call(url=url, data={"course_id": course_id})


def get_result(url, token):
    """
    Get result from xanalytics for token.
    Args:
        token (unicode): Token from xanalytics job.
    Returns:
        data (dict): Dictionary from JSON object provided by xanalytics.
    """
    return _call(url=url, data={"token": token})
