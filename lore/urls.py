"""lore URL Configuration

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
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin

import importer.urls as importer_urls
import cas.urls as cas_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^importer/', include(importer_urls)),
    url(r'^cas/', include(cas_urls)),
]
