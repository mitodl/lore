"""
Controllers for REST app
"""

from __future__ import unicode_literals
from operator import itemgetter

from django.http.response import Http404
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from roles.permissions import GroupTypes, BaseGroupTypes
from roles.api import (
    assign_user_to_repo_group,
    remove_user_from_repo_group,
    list_users_in_repo,
    is_last_admin_in_repo,
)
from rest.serializers import (
    VocabularySerializer,
    RepositorySerializer,
    TermSerializer,
    UserGroupSerializer,
    UserSerializer,
    GroupSerializer,
    LearningResourceSerializer,
    StaticAssetSerializer,
)
from rest.permissions import (
    AddRepoPermission,
    AddEditMetadataPermission,
    ViewRepoPermission,
    ViewVocabularyPermission,
    ViewTermPermission,
    ManageTaxonomyPermission,
    ManageRepoMembersPermission,
    ViewLearningResourcePermission,
    ViewStaticAssetPermission,
)
from rest.util import CheckValidMemberParamMixin
from taxonomy.models import Vocabulary
from learningresources.models import (
    Repository,
    LearningResource,
    StaticAsset,
)
from learningresources.api import (
    get_repos,
)


def get_urls(raw_urls, list_urls=None, urlbase=''):
    """
    Recursively builds a list of all the urls in the current project and
    the name of their associated view
    """
    list_urls = list_urls or []
    for entry in raw_urls:
        full_url = (urlbase + entry.regex.pattern).replace('^', '')
        if '$' in full_url:
            full_url = full_url[0: full_url.index("$")]

        full_url = full_url.replace("(?P", "")
        full_url = full_url.replace("[-\\w]+)", "")
        full_url = full_url.replace("\\d+)", "")

        if entry.callback:  # if it points to a view
            list_urls.append({"api": full_url})
        else:  # if it points to another urlconf, recur!
            get_urls(entry.url_patterns, list_urls, full_url)

    # sort alphabetically
    list_urls.sort(key=itemgetter('api'))
    return list_urls


@api_view(('GET',))
def index(request):
    """
    Root service , returns list of end points
    """
    import rest.urls as rest_urls
    list_urls = get_urls(
        rest_urls.urlpatterns, urlbase=request.path
    )
    return Response(list_urls)


# pylint: disable=too-many-ancestors
class RepositoryList(ListCreateAPIView):
    """REST list view for Repository"""
    serializer_class = RepositorySerializer
    permission_classes = (
        AddRepoPermission,
        IsAuthenticated,
    )

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('repository-detail', kwargs={'repo_slug': data['slug']})
        return {'Location': url}

    def get_queryset(self):
        """Filter to these repositories"""

        repo_ids = [repo.id for repo in get_repos(self.request.user.id)]
        return Repository.objects.filter(id__in=repo_ids).order_by('id')

    def perform_create(self, serializer):
        """Create a new repository"""
        # pylint: disable=protected-access
        repo = serializer.save()
        assign_user_to_repo_group(
            self.request.user,
            repo,
            GroupTypes.REPO_ADMINISTRATOR
        )


class RepositoryDetail(RetrieveAPIView):
    """REST detail view for Repository"""
    serializer_class = RepositorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'repo_slug'
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to this repository"""
        return Repository.objects.filter(slug=self.kwargs['repo_slug'])


class VocabularyList(ListCreateAPIView):
    """REST list view for Vocabulary"""
    serializer_class = VocabularySerializer
    permission_classes = (
        ViewRepoPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter vocabularies by repository ownership and optionally
        by learning resource type"""
        queryset = Vocabulary.objects.filter(
            repository__slug=self.kwargs['repo_slug']
        )
        learning_resource_type = self.request.query_params.get(
            'type_name', None)
        if learning_resource_type is not None:
            queryset = queryset.filter(
                learning_resource_types__name=learning_resource_type)
        return queryset.order_by('id')

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('vocabulary-detail', kwargs={
            'repo_slug': self.kwargs['repo_slug'],
            'vocab_slug': data['slug'],
        })
        return {'Location': url}


class VocabularyDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Vocabulary"""
    serializer_class = VocabularySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'vocab_slug'
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a vocabulary within a repository"""
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        return repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )


class TermList(ListCreateAPIView):
    """REST list view for Term"""
    serializer_class = TermSerializer
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to terms within a vocabulary and repository"""

        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        vocabs = repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )
        if not vocabs.exists():
            return []

        return vocabs.first().term_set.order_by('id')

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('term-detail', kwargs={
            'vocab_slug': self.kwargs['vocab_slug'],
            'repo_slug': self.kwargs['repo_slug'],
            'term_slug': data['slug'],
        })
        return {'Location': url}


class TermDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Term"""
    serializer_class = TermSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'term_slug'
    permission_classes = (
        ViewTermPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a term within a vocabulary within a repository"""
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        vocabs = repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )
        if not vocabs.exists():
            return []

        return vocabs.first().term_set.filter(
            slug=self.kwargs['term_slug']
        )


class RepoMemberList(ListAPIView):
    """
    REST list view for repository members
    """
    serializer_class = UserGroupSerializer
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Return a list of repository members
        """
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        return list_users_in_repo(repo)


class RepoMemberGroupList(CheckValidMemberParamMixin, ListCreateAPIView):
    """
    REST list view for repository members per group
    """
    serializer_class = UserSerializer
    permission_classes = (
        ManageRepoMembersPermission,
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Return a list of repository members
        """
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        group_type = self.kwargs.get('group_type')
        return list_users_in_repo(repo, group_type)

    def perform_create(self, serializer):
        """Add a user in the group"""
        # Validate the incoming data
        serializer.is_valid(raise_exception=True)
        # Get the user
        username = serializer.data.get('username')
        user = User.objects.get(username=username)
        # Get the repo group type
        group_type = self.kwargs.get('group_type')
        repo_group_type = GroupTypes.get_repo_groupname_by_base(group_type)
        # Get the repo object
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        assign_user_to_repo_group(user, repo, repo_group_type)

    def get_success_headers(self, data):
        """
        Add Location header for create
        """
        url = reverse(
            'repo-members-group-user-detail',
            kwargs={
                'repo_slug': self.kwargs['repo_slug'],
                'username': data['username'],
                'group_type': self.kwargs.get('group_type'),
            }
        )
        return {'Location': url}


class RepoMemberUserList(CheckValidMemberParamMixin, ListCreateAPIView):
    """
    REST group list view for a repository member
    """
    serializer_class = GroupSerializer
    permission_classes = (
        ManageRepoMembersPermission,
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Return groups for a repository member
        """
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        username = self.kwargs.get('username')
        return list(
            set(
                user_group for user_group in list_users_in_repo(repo)
                if user_group.username == username
            )
        )

    def perform_create(self, serializer):
        """Add a group for a user"""
        # Validate the incoming data
        serializer.is_valid(raise_exception=True)
        # Get the user
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        # Get the repo group type
        group_type = serializer.data.get('group_type')
        repo_group_type = GroupTypes.get_repo_groupname_by_base(group_type)
        # Get the repo object
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        assign_user_to_repo_group(user, repo, repo_group_type)

    def get_success_headers(self, data):
        """
        Add Location header for create
        """
        url = reverse(
            'repo-members-user-group-detail',
            kwargs={
                'repo_slug': self.kwargs['repo_slug'],
                'group_type': data['group_type'],
                'username': self.kwargs.get('username'),
            }
        )
        return {'Location': url}


class RepoMemberUserGroupDetail(CheckValidMemberParamMixin,
                                RetrieveDestroyAPIView):
    """
    REST for one group assigned to a user in a repository
    """
    serializer_class = GroupSerializer
    permission_classes = (
        ManageRepoMembersPermission,
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_object(self):
        """
        Return details about a group for a user in a repo
        """
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        username = self.kwargs.get('username')
        group_type = self.kwargs.get('group_type')
        user_groups = list_users_in_repo(repo, group_type)
        # There can be max only one user with the specified username in a group
        for user_group in user_groups:
            if user_group.username == username:
                return user_group
        raise Http404()

    def delete(self, request, *args, **kwargs):
        """
        Delete a group for a user in a repo
        """
        # Get the user
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        # Get the repo group type
        group_type = self.kwargs.get('group_type')
        repo_group_type = GroupTypes.get_repo_groupname_by_base(group_type)
        # Get the repo object
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        # if the group is administrators and this user is the last one
        # forbid to delete
        if (group_type == BaseGroupTypes.ADMINISTRATORS and
                is_last_admin_in_repo(user, repo)):
            return Response(
                data={
                    "detail": ("This is the last "
                               "administrator of the repository")
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        remove_user_from_repo_group(user, repo, repo_group_type)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepoMemberGroupUserDetail(RepoMemberUserGroupDetail):
    """
    REST for one user assigned to a group in a repository
    """
    serializer_class = UserSerializer


class LearningResourceList(ListAPIView):
    """REST list view for LearningResource"""
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'lr_id'
    permission_classes = (
        ViewRepoPermission,
        AddEditMetadataPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get queryset for a learning resource"""
        return LearningResource.objects.filter(
            course__repository__slug=self.kwargs['repo_slug']
        )


class LearningResourceDetail(RetrieveUpdateAPIView):
    """REST detail view for LearningResource"""
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'lr_id'
    permission_classes = (
        ViewLearningResourcePermission,
        AddEditMetadataPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get queryset for a learning resource"""
        return LearningResource.objects.filter(
            id=self.kwargs['lr_id'])


class StaticAssetList(ListAPIView):
    """REST list view for StaticAsset"""
    serializer_class = StaticAssetSerializer
    permission_classes = (
        ViewLearningResourcePermission,
        IsAuthenticated
    )
    lookup_field = 'id'
    lookup_url_kwarg = 'sa_id'

    def get_queryset(self):
        """Get queryset for static assets for a particular learning resource"""
        return LearningResource.objects.get(
            id=self.kwargs['lr_id']
        ).static_assets.filter()


class StaticAssetDetail(RetrieveAPIView):
    """REST list view for StaticAsset"""
    serializer_class = StaticAssetSerializer
    permission_classes = (
        ViewStaticAssetPermission,
        IsAuthenticated
    )
    lookup_field = 'id'
    lookup_url_kwarg = 'sa_id'

    def get_queryset(self):
        """Get queryset for static assets for a particular learning resource"""
        return StaticAsset.objects.filter(
            id=self.kwargs['sa_id']
        )
