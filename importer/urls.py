"""
URLs for the importer app.
"""

from __future__ import unicode_literals

from django.conf.urls import url

from importer.views import status, upload

urlpatterns = [
    url(r'^status/$', status, name='status'),
    url(r'^upload/$', upload, name='upload'),
]
