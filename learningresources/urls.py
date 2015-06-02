"""
URLs for the importer app.
"""

from __future__ import unicode_literals

from django.conf.urls import url

from learningresources.views import welcome, create_repo, listing

urlpatterns = [
    url(r'^$', welcome, name='welcome'),
    url(r'^welcome/$', welcome, name='welcome'),
    url(r'^create_repo/$', create_repo, name='create_repo'),
    url(r'^listing/(?P<repo_id>\d+)/(?P<page>\d+)', listing, name='listing'),
]
