"""
URLs for REST application
"""

from __future__ import unicode_literals

from django.conf.urls import url, include

from .views import (
    CourseDetail,
    CourseList,
    LearningResourceDetail,
    LearningResourceExportDetail,
    LearningResourceExportList,
    LearningResourceExportTaskDetail,
    LearningResourceExportTaskList,
    TaskDetail,
    TaskList,
    LearningResourceList,
    LearningResourceTypeList,
    RepoMemberGroupList,
    RepoMemberGroupUserDetail,
    RepoMemberList,
    RepoMemberUserGroupDetail,
    RepoMemberUserList,
    RepositoryDetail,
    RepositoryList,
    RepositorySearchList,
    StaticAssetDetail,
    StaticAssetList,
    TermDetail,
    TermList,
    VocabularyDetail,
    VocabularyList,
)

REPOSITORY_MEMBERS_URL = r'^repositories/(?P<repo_slug>[-\w]+)/members/'
REPOSITORY_VOCAB_URL = r'^repositories/(?P<repo_slug>[-\w]+)/vocabularies/'
REPOSITORY_RESOURCE_URL = (
    r'^repositories/(?P<repo_slug>[-\w]+)/learning_resources/'
)
REPOSITORY_EXPORTS_URL = (
    r'^repositories/(?P<repo_slug>[-\w]+)/learning_resource_exports/'
)
REPOSITORY_EXPORT_TASK_URL = (
    r'^repositories/(?P<repo_slug>[-\w]+)/learning_resource_export_tasks/'
)
TASK_URL = r'^tasks/'
REPOSITORY_SEARCH_URL = r'^repositories/(?P<repo_slug>[-\w]+)/search/'

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^repositories/$',
        RepositoryList.as_view(),
        name='repository-list'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/$',
        RepositoryDetail.as_view(),
        name='repository-detail'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/courses/$',
        CourseList.as_view(),
        name='course-list'),
    url(r'^repositories/(?P<repo_slug>[-\w]+)/courses/(?P<course_id>\d+)/$',
        CourseDetail.as_view(),
        name='course-detail'),
    url(REPOSITORY_VOCAB_URL + r'$',
        VocabularyList.as_view(),
        name='vocabulary-list'),
    url(REPOSITORY_VOCAB_URL + r'(?P<vocab_slug>[-\w]+)/$',
        VocabularyDetail.as_view(),
        name='vocabulary-detail'),
    url(REPOSITORY_VOCAB_URL + r'(?P<vocab_slug>[-\w]+)/terms/$',
        TermList.as_view(),
        name='term-list'),
    url(REPOSITORY_VOCAB_URL +
        r'(?P<vocab_slug>[-\w]+)/terms/(?P<term_slug>[-\w]+)/$',
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
    url(REPOSITORY_RESOURCE_URL + r'$',
        LearningResourceList.as_view(),
        name='learning-resource-list'),
    url(REPOSITORY_RESOURCE_URL + r'(?P<lr_id>\d+)/$',
        LearningResourceDetail.as_view(),
        name='learning-resource-detail'),
    url(REPOSITORY_RESOURCE_URL + r'(?P<lr_id>\d+)/static_assets/$',
        StaticAssetList.as_view(),
        name='static-asset-list'),
    url(REPOSITORY_RESOURCE_URL +
        r'(?P<lr_id>\d+)/static_assets/(?P<sa_id>\d+)/$',
        StaticAssetDetail.as_view(),
        name='static-asset-detail'),
    url(REPOSITORY_EXPORTS_URL + r'(?P<username>[-\w]+)/$',
        LearningResourceExportList.as_view(),
        name='learning-resource-export-list'),
    url(REPOSITORY_EXPORTS_URL + r'(?P<username>[-\w]+)/(?P<lr_id>\d+)/$',
        LearningResourceExportDetail.as_view(),
        name='learning-resource-export-detail'),
    url(REPOSITORY_EXPORT_TASK_URL + r'$',
        LearningResourceExportTaskList.as_view(),
        name='learning-resource-export-task-list'),
    url(REPOSITORY_EXPORT_TASK_URL + r'(?P<task_id>[-\w]+)/$',
        LearningResourceExportTaskDetail.as_view(),
        name='learning-resource-export-task-detail'),
    url(TASK_URL + r'$',
        TaskList.as_view(),
        name='task-list'),
    url(TASK_URL + r'(?P<task_id>[-\w]+)/$',
        TaskDetail.as_view(),
        name='task-detail'),
    url("^learning_resource_types/$", LearningResourceTypeList.as_view(),
        name='learning-resource-type-list'),
    url(REPOSITORY_SEARCH_URL, RepositorySearchList.as_view({'get': 'list'}),
        name="repository-search-list"),
]
