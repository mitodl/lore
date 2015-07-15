"""
lore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))"""

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from search.forms import SearchForm
from ui.views import (
    welcome, create_repo, export,
    upload, edit_vocabulary, create_vocabulary,
    RepositoryView, serve_media
)
import rest.urls as rest_urls
import cas.urls as cas_urls


urlpatterns = [
    url(r'^$', welcome, name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(rest_urls)),
    url(r'^cas/', include(cas_urls)),
    url(r'^home/$', welcome, name='welcome'),
    url(r'^repositories/new/$', create_repo, name='create_repo'),
    url(
        r'^repositories/(?P<repo_slug>[-\w]+)/$',
        login_required(
            RepositoryView(
                form_class=SearchForm, template="repository.html",
            )
        ),
        name='repositories'
    ),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/'
        r'learningresources/(?P<resource_id>\d+)/$',
        export,
        name='export'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/import/$',
        upload, name='upload'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/vocabularies/$',
        create_vocabulary,
        name="create_vocabulary"),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/'
        r'vocabularies/(?P<vocab_slug>[-\w]+)/$',
        edit_vocabulary,
        name="edit_vocabulary"),
]

if (settings.DEFAULT_FILE_STORAGE ==
        'django.core.files.storage.FileSystemStorage'):
    urlpatterns.append(
        url(r'^media/(?P<media_path>.+)$',
            serve_media,
            name='media')
    )
