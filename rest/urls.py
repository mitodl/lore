"""
URLs for REST application
"""

from __future__ import unicode_literals

from django.conf.urls import url, include

from .views import (
    RepositoryList,
    RepositoryDetail,
    VocabularyList,
    VocabularyDetail,
    TermList,
    TermDetail,
)

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^repositories/$',
        RepositoryList.as_view(),
        name='repository-list'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/$',
        RepositoryDetail.as_view(),
        name='repository-detail'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/vocabularies/$',
        VocabularyList.as_view(),
        name='vocabulary-list'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/'
        r'vocabularies/(?P<vocab_slug>[-\w]+)/$',
        VocabularyDetail.as_view(),
        name='vocabulary-detail'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/'
        r'vocabularies/(?P<vocab_slug>[-\w]+)/terms/$',
        TermList.as_view(),
        name='term-list'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/'
        r'vocabularies/(?P<vocab_slug>[-\w]+)/terms/(?P<term_slug>[-\w]+)/$',
        TermDetail.as_view(),
        name='term-detail'),
]
