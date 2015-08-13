"""
Status checks for LORE.

Notes:

* Useful messages are logged, but NO_CONFIG is returned whether
  settings are missing or invalid, to prevent information leakage.
* Different services provide different information, but all should return
  "up," DOWN, or NO_CONFIG for the "status" key.
"""

from datetime import datetime
import logging

from django.conf import settings
from django.http import JsonResponse, Http404
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from kombu.utils.url import _parse_url as parse_redis_url
from psycopg2 import connect, OperationalError
from redis import (
    StrictRedis,
    ConnectionError as RedisConnectionError,
    ResponseError as RedisResponseError,
)

log = logging.getLogger(__name__)

UP = "up"
DOWN = "down"
NO_CONFIG = "no config found"
HTTP_OK = 200
SERVICE_UNAVAILABLE = 503
TIMEOUT_SECONDS = 5


def get_pg_info():
    """Check PostgreSQL connection."""
    log.debug("entered get_pg_info")
    try:
        conf = settings.DATABASES['default']
        database = conf["NAME"]
        user = conf["USER"]
        host = conf["HOST"]
        port = conf["PORT"]
        password = conf["PASSWORD"]
    except (AttributeError, KeyError):
        log.error("No PostgreSQL connection info found in settings.")
        return {"status": NO_CONFIG}
    except TypeError:
        return {"status": DOWN}
    log.debug("got past getting conf")
    try:
        start = datetime.now()
        connection = connect(
            database=database, user=user, host=host,
            port=port, password=password, connect_timeout=TIMEOUT_SECONDS,
        )
        log.debug("at end of context manager")
        micro = (datetime.now() - start).microseconds
        connection.close()
    except (OperationalError, KeyError):
        log.error("Invalid PostgreSQL connection info in settings: %s", conf)
        return {"status": DOWN}
    log.debug("got to end of postgres check successfully")
    return {"status": UP, "response_microseconds": micro}


def get_redis_info():
    """Check Redis connection."""
    try:
        url = settings.BROKER_URL
        _, host, port, _, _, db, _ = parse_redis_url(url)
    except AttributeError:
        log.error("No valid Redis connection info found in settings.")
        return {"status": NO_CONFIG}

    start = datetime.now()
    try:
        rdb = StrictRedis(
            host=host, port=port, db=db, socket_timeout=TIMEOUT_SECONDS)
        info = rdb.info()
    except (RedisConnectionError, TypeError) as ex:
        log.error("Error making Redis connection: %s", ex.args)
        return {"status": DOWN}
    except RedisResponseError as ex:
        log.error("Bad Redis response: %s", ex.args)
        return {"status": DOWN, "message": "auth error"}
    micro = (datetime.now() - start).microseconds
    del rdb  # the redis package does not support Redis's QUIT.
    ret = {
        "status": UP, "response_microseconds": micro,
    }
    fields = ("uptime_in_seconds", "used_memory", "used_memory_peak")
    ret.update({x: info[x] for x in fields})
    return ret


def get_elasticsearch_info():
    """Check Elasticsearch connection."""
    try:
        url = settings.HAYSTACK_CONNECTIONS["default"]["URL"]
    except (AttributeError, KeyError):
        log.error("No Elasticsearch connection info in settings.")
        return {"status": NO_CONFIG}
    start = datetime.now()
    try:
        search = Elasticsearch(url, request_timeout=TIMEOUT_SECONDS)
        info = search.info()
    except ESConnectionError:
        return {"status": DOWN}
    del search  # The elasticsearch library has no "close" or "disconnect."
    micro = (datetime.now() - start).microseconds
    return {
        "status": UP, "response_microseconds": micro,
        "status_code": info["status"],
    }


def status(request):  # pylint: disable=unused-argument
    """Status"""
    token = request.GET.get("token", "")
    if token != settings.STATUS_TOKEN:
        raise Http404()
    info = {}
    log.debug("going to get redis")
    info["redis"] = get_redis_info()
    log.debug("redis done, going for elasticsearch")
    info["elasticsearch"] = get_elasticsearch_info()
    log.debug("elasticsearch done, hunting postgres")
    info["postgresql"] = get_pg_info()
    code = HTTP_OK
    for key in info:
        if info[key]["status"] == "down":
            code = SERVICE_UNAVAILABLE
            break
    resp = JsonResponse(info)
    resp.status_code = code
    return resp
