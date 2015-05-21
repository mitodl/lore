"""
URLs for taxonomy app
"""
from django.conf.urls import url

from taxonomy.views import (
    create_vocabulary,
    edit_vocabulary,
)

urlpatterns = [
    url(r'^vocabulary/$', create_vocabulary, name="create_vocabulary"),
    url(r'^vocabulary/(?P<vocabulary_id>[0-9]+)/$', edit_vocabulary,
        name="edit_vocabulary"),
]
