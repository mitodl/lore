"""
Celery tasks for the search module.
"""

from __future__ import unicode_literals

from datetime import datetime

from elasticsearch_dsl.connections import connections
from lore.celery import async
from statsd.defaults.django import statsd


@async.task
@statsd.timer('lore.search.tasks.refresh_index')
def refresh_index():
    """
    Refresh the Elasticsearch index via Celery.
    """
    conn = connections.get_connection()
    with open("refresh.log", "ab") as raw:
        raw.write("{0} _refresh_index ran\n".format(datetime.now()))
    conn.indices.refresh(index=INDEX_NAME)
