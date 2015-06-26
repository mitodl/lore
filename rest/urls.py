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
    RepoMemberList,
    RepoMemberGroupList,
    RepoMemberUserList,
    RepoMemberUserGroupDetail,
    RepoMemberGroupUserDetail,
)

REPOSITORY_MEMBERS_URL = r'^repositories/(?P<repo_slug>[-\w]+)/members/'

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
    # Section for repository group members
    url(
        REPOSITORY_MEMBERS_URL + r'$',
        RepoMemberList.as_view(),
        name='repo-members'
    ),
    url(
        REPOSITORY_MEMBERS_URL +
        r'groups/(?P<group_type>[-\w]+)/users/$',
        RepoMemberGroupList.as_view(),
        name='repo-members-group'
    ),
    url(
        REPOSITORY_MEMBERS_URL +
        r'groups/(?P<group_type>[-\w]+)/users/(?P<username>[-\w]+)/$',
        RepoMemberGroupUserDetail.as_view(),
        name='repo-members-group-user-detail'
    ),
    url(
        REPOSITORY_MEMBERS_URL +
        r'users/(?P<username>[-\w]+)/groups/$',
        RepoMemberUserList.as_view(),
        name='repo-members-user'
    ),
    url(
        REPOSITORY_MEMBERS_URL +
        r'users/(?P<username>[-\w]+)/groups/(?P<group_type>[-\w]+)/$',
        RepoMemberUserGroupDetail.as_view(),
        name='repo-members-user-group-detail'
    ),
]
