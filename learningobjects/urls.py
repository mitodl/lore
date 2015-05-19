"""
URLs for the learningobjects app.
"""
from django.conf.urls import url, patterns

from learningobjects.views import create_repo

urlpatterns = patterns(
    "",
    url(r'^create_repo/$', create_repo, name='create_repo'),
)
