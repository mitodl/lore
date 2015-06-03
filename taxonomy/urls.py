"""
URLs for taxonomy app
"""
from __future__ import unicode_literals
from django.conf.urls import url

from taxonomy.views import (
    create_vocabulary,
    edit_vocabulary,
)

urlpatterns = [
    url(r'^(?P<repository_id>[0-9]+)/vocabulary/$',
        create_vocabulary,
        name="create_vocabulary"),
    url(r'^(?P<repository_id>[0-9]+)/vocabulary/(?P<vocabulary_id>[0-9]+)$',
        edit_vocabulary,
        name="edit_vocabulary"),
]
