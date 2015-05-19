"""
URLs for the importer app.
"""
from django.conf.urls import url, patterns

from importer.views import status, upload

urlpatterns = patterns(
    "",
    url(r'^status/$', status, name='status'),
    url(r'^upload/$', upload, name='upload'),
)
