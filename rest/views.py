"""
Controllers for REST app
"""

from __future__ import unicode_literals

from django.http.response import Http404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.exceptions import ValidationError
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
from celery.states import FAILURE, SUCCESS, REVOKED
from celery.result import AsyncResult

from exporter.tasks import export_resources
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
    LearningResourceTypeSerializer,
    LearningResourceSerializer,
    LearningResourceExportSerializer,
    LearningResourceExportTaskSerializer,
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
    ViewLearningResourceExportPermission,
    ViewStaticAssetPermission,
)
from rest.util import CheckValidMemberParamMixin
from taxonomy.models import Vocabulary
from learningresources.models import (
    Repository,
    LearningResourceType,
    LearningResource,
    StaticAsset,
)
from learningresources.api import (
    get_repos,
    get_resource,
)

EXPORTS_KEY = 'learning_resource_exports'
EXPORT_TASK_KEY = 'learning_resource_export_tasks'


class RepositoryList(ListCreateAPIView):
    """REST list view for Repository."""
    serializer_class = RepositorySerializer
    permission_classes = (
        AddRepoPermission,
        IsAuthenticated,
    )

    def get_success_headers(self, data):
        """Add Location header for model create."""
        url = reverse('repository-detail', kwargs={'repo_slug': data['slug']})
        return {'Location': url}

    def get_queryset(self):
        """Filter to these repositories."""

        repo_ids = [repo.id for repo in get_repos(self.request.user.id)]
        return Repository.objects.filter(id__in=repo_ids).order_by('id')

    def perform_create(self, serializer):
        """Create a new repository."""
        # pylint: disable=protected-access
        repo = serializer.save()
        assign_user_to_repo_group(
            self.request.user,
            repo,
            GroupTypes.REPO_ADMINISTRATOR
        )


class RepositoryDetail(RetrieveAPIView):
    """REST detail view for Repository."""
    serializer_class = RepositorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'repo_slug'
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to this repository."""
        return Repository.objects.filter(slug=self.kwargs['repo_slug'])


class VocabularyList(ListCreateAPIView):
    """REST list view for Vocabulary."""
    serializer_class = VocabularySerializer
    permission_classes = (
        ViewRepoPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter vocabularies by repository ownership and optionally
        by LearningResource type."""
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
        """Add Location header for model create."""
        url = reverse('vocabulary-detail', kwargs={
            'repo_slug': self.kwargs['repo_slug'],
            'vocab_slug': data['slug'],
        })
        return {'Location': url}


class VocabularyDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Vocabulary."""
    serializer_class = VocabularySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'vocab_slug'
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a vocabulary within a repository."""
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        return repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )


class TermList(ListCreateAPIView):
    """REST list view for Term."""
    serializer_class = TermSerializer
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to terms within a vocabulary and repository."""

        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        vocabs = repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )
        if not vocabs.exists():
            return []

        return vocabs.first().term_set.order_by('id')

    def get_success_headers(self, data):
        """Add Location header for model create."""
        url = reverse('term-detail', kwargs={
            'vocab_slug': self.kwargs['vocab_slug'],
            'repo_slug': self.kwargs['repo_slug'],
            'term_slug': data['slug'],
        })
        return {'Location': url}


class TermDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Term."""
    serializer_class = TermSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'term_slug'
    permission_classes = (
        ViewTermPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a term within a vocabulary within a repository."""
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
        """Add a user in the group."""
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
        """Add a group for a user."""
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


class LearningResourceTypeList(ListAPIView):
    """REST list view for LearningResourceType."""
    serializer_class = LearningResourceTypeSerializer
    queryset = LearningResourceType.objects.all()


class LearningResourceList(ListAPIView):
    """REST list view for LearningResource."""
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'lr_id'
    permission_classes = (
        ViewRepoPermission,
        AddEditMetadataPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get queryset for a LearningResource."""
        queryset = LearningResource.objects.filter(
            course__repository__slug=self.kwargs['repo_slug']
        )
        id_value = self.request.query_params.get('id', None)
        if id_value is not None:
            try:
                id_list = [int(x) for x in id_value.split(',') if len(x) > 0]
            except ValueError:
                raise ValidationError("id is not a number")
            queryset = queryset.filter(id__in=id_list)
        return queryset


class LearningResourceDetail(RetrieveUpdateAPIView):
    """REST detail view for LearningResource."""
    serializer_class = LearningResourceSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'lr_id'
    permission_classes = (
        ViewLearningResourcePermission,
        AddEditMetadataPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get queryset for a LearningResource."""
        return LearningResource.objects.filter(
            id=self.kwargs['lr_id'])


class StaticAssetList(ListAPIView):
    """REST list view for StaticAsset."""
    serializer_class = StaticAssetSerializer
    permission_classes = (
        ViewLearningResourcePermission,
        IsAuthenticated
    )
    lookup_field = 'id'
    lookup_url_kwarg = 'sa_id'

    def get_queryset(self):
        """Get queryset for static assets for a particular LearningResource."""
        return LearningResource.objects.get(
            id=self.kwargs['lr_id']
        ).static_assets.filter()


class StaticAssetDetail(RetrieveAPIView):
    """REST list view for StaticAsset."""
    serializer_class = StaticAssetSerializer
    permission_classes = (
        ViewStaticAssetPermission,
        IsAuthenticated
    )
    lookup_field = 'id'
    lookup_url_kwarg = 'sa_id'

    def get_queryset(self):
        """Get queryset for static assets for a particular LearningResource."""
        return StaticAsset.objects.filter(
            id=self.kwargs['sa_id']
        )


class LearningResourceExportList(ListCreateAPIView):
    """REST list view for exports."""

    serializer_class = LearningResourceExportSerializer
    permission_classes = (
        ViewLearningResourceExportPermission,
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        repo_slug = self.kwargs['repo_slug']
        try:
            exports = self.request.session[
                EXPORTS_KEY][repo_slug]
        except KeyError:
            exports = []
        return [{"id": lr_id} for lr_id in exports]

    def create(self, request, *args, **kwargs):
        try:
            lr_id = int(request.data['id'])
        except ValueError:
            raise ValidationError("LearningResource id must be a number")
        repo_slug = self.kwargs['repo_slug']

        learning_resource = get_resource(lr_id, self.request.user.id)
        if learning_resource.course.repository.slug != repo_slug:
            raise PermissionDenied()

        if EXPORTS_KEY not in self.request.session:
            self.request.session[EXPORTS_KEY] = {}

        if repo_slug not in self.request.session[EXPORTS_KEY]:
            self.request.session[EXPORTS_KEY][repo_slug] = []

        exports = self.request.session[EXPORTS_KEY][repo_slug]
        if lr_id not in exports:
            exports.append(lr_id)
            self.request.session.modified = True

        url = reverse('learning-resource-export-detail',
                      kwargs={'repo_slug': self.kwargs['repo_slug'],
                              'username': self.kwargs['username'],
                              'lr_id': lr_id})
        headers = {"Location": url}
        return Response(
            {"id": lr_id}, status=status.HTTP_201_CREATED, headers=headers)

    # pylint: disable=unused-argument
    def delete(self, request, *args, **kwargs):
        """Delete all ids in session for this repository and user."""
        try:
            del self.request.session[EXPORTS_KEY][self.kwargs['repo_slug']]
            self.request.session.modified = True
        except KeyError:
            # doesn't exist, no need to delete
            pass
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            content_type="text"
        )


class LearningResourceExportDetail(RetrieveDestroyAPIView):
    """
    Detail resource for a LearningResource id for export
    """
    serializer_class = LearningResourceExportSerializer
    permission_classes = (
        ViewLearningResourceExportPermission,
        ViewLearningResourcePermission,
        IsAuthenticated,
    )
    lookup_field = 'id'
    lookup_url_kwarg = 'lr_id'

    def get_object(self):
        """
        Retrieve an export id from the list.
        """
        try:
            lr_id = int(self.kwargs['lr_id'])
        except ValueError:
            raise Http404

        repo_slug = self.kwargs['repo_slug']
        try:
            exports = self.request.session[
                EXPORTS_KEY][repo_slug]
        except KeyError:
            raise Http404

        if lr_id not in exports:
            raise Http404

        return {"id": lr_id}

    def perform_destroy(self, instance):
        """
        Delete an export id from our export list.
        """
        lr_id = instance['id']
        repo_slug = self.kwargs['repo_slug']
        try:
            exports = self.request.session[
                EXPORTS_KEY][repo_slug]
            if lr_id in exports:
                exports.remove(lr_id)
                self.request.session.modified = True
        except KeyError:
            raise Http404


def create_task_result_dict(task):
    """
    Convert initial data we put in session to dict for REST API.
    This will use the id to look up current data about task to return
    to user.

    Args:
        task (dict): Initial data about task stored in session.
    Returns:
        dict: Current data about task.
    """
    initial_state = task['initial_state']
    task_id = task['id']

    state = "processing"
    url = ""
    # initial_state is a workaround for EagerResult used in testing.
    # In production initial_state should usually be pending.
    if initial_state == SUCCESS:
        state = "success"
        url = task['url']
    elif initial_state == FAILURE or initial_state == REVOKED:
        state = "failure"
    else:
        result = AsyncResult(task_id)

        if result.successful():
            state = "success"
        elif result.failed():
            state = "failure"

        if result.successful():
            url = default_storage.url(result.get())

    return {
        "id": task_id,
        "status": state,
        "url": url
    }


class LearningResourceExportTaskList(ListCreateAPIView):
    """
    View for export tasks for a user.
    """
    serializer_class = LearningResourceExportTaskSerializer
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get tasks for this user."""
        repo_slug = self.kwargs['repo_slug']
        try:
            tasks = self.request.session[EXPORT_TASK_KEY][repo_slug]
        except KeyError:
            tasks = {}

        return [create_task_result_dict(task) for task in tasks.values()]

    def post(self, request, *args, **kwargs):
        """
        Create a new export task for this user.

        Note that this also cancels and clears any old tasks for the user,
        so there should be only one task in the list at any time.

        The export list will be left alone. Once the list is exported
        the client may DELETE the export list as a separate REST call.
        """

        repo_slug = self.kwargs['repo_slug']
        try:
            exports = self.request.session[EXPORTS_KEY][repo_slug]
        except KeyError:
            exports = []

        # Cancel any old tasks.
        old_tasks = self.request.session.get(
            EXPORT_TASK_KEY, {}).get(repo_slug, {})
        for task_id in old_tasks.keys():
            AsyncResult(task_id).revoke()

        # Clear task list.
        if EXPORT_TASK_KEY not in self.request.session:
            self.request.session[EXPORT_TASK_KEY] = {}
        self.request.session[EXPORT_TASK_KEY][repo_slug] = {}

        learning_resources = LearningResource.objects.filter(
            id__in=exports).all()
        result = export_resources.delay(
            learning_resources, self.request.user.username)

        if result.successful():
            url = default_storage.url(result.get())
        else:
            url = ""

        # Put new task in session.
        self.request.session[EXPORT_TASK_KEY][repo_slug][result.id] = {
            "id": result.id,
            "initial_state": result.state,
            "url": url
        }
        self.request.session.modified = True

        return Response(
            {"id": result.id},
            status=status.HTTP_201_CREATED
        )


class LearningResourceExportTaskDetail(RetrieveAPIView):
    """
    Detail view for a user's export tasks.
    """
    serializer_class = LearningResourceExportTaskSerializer
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_object(self):
        """
        Retrieve current information about an export task.
        """
        try:
            task_id = self.kwargs['task_id']
        except ValueError:
            raise Http404

        repo_slug = self.kwargs['repo_slug']
        try:
            initial_dict = self.request.session[
                EXPORT_TASK_KEY][repo_slug][task_id]
        except KeyError:
            raise Http404

        return create_task_result_dict(initial_dict)
