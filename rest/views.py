"""
Controllers for REST app
"""

from __future__ import unicode_literals

from django.http.response import Http404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from statsd.defaults.django import statsd

from learningresources.api import (
    PermissionDenied,
    NotFound,
)
from roles.permissions import GroupTypes, BaseGroupTypes
from roles.api import (
    assign_user_to_repo_group,
    is_last_admin_in_repo,
    list_users_in_repo,
    remove_user_from_repo_group,
)
from rest.serializers import (
    CourseSerializer,
    GroupSerializer,
    LearningResourceExportSerializer,
    LearningResourceExportTaskSerializer,
    TaskSerializer,
    LearningResourceSerializer,
    LearningResourceTypeSerializer,
    RepositorySearchSerializer,
    RepositorySerializer,
    StaticAssetSerializer,
    TermSerializer,
    UserGroupSerializer,
    UserSerializer,
    VocabularySerializer,
)
from rest.permissions import (
    AddEditMetadataPermission,
    AddRepoPermission,
    ImportCoursePermission,
    ManageRepoMembersPermission,
    ManageTaxonomyPermission,
    ViewLearningResourceExportPermission,
    ViewLearningResourcePermission,
    ViewRepoPermission,
    ViewStaticAssetPermission,
    ViewTermPermission,
    ViewVocabularyPermission,
)
from rest.tasks import (
    create_task,
    create_task_result_dict,
    get_task,
    get_tasks,
    remove_task,
    EXPORTS_KEY,
    EXPORT_TASK_TYPE,
)
from rest.util import CheckValidMemberParamMixin
from search.api import construct_queryset
from search.tasks import index_resources
from taxonomy.models import Vocabulary
from learningresources.models import (
    Repository,
    Course,
    LearningResourceType,
    LearningResource,
    StaticAsset,
)
from learningresources.api import (
    get_repos,
    get_resource,
)


# pylint: disable=too-many-lines
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


class CourseList(ListAPIView):
    """REST list view for Courses."""
    serializer_class = CourseSerializer
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Filter coursed by repository
        """
        queryset = Course.objects.filter(
            repository__slug=self.kwargs['repo_slug'])
        return queryset.order_by('id')


class CourseDetail(RetrieveDestroyAPIView):
    """REST detail for Course"""
    serializer_class = CourseSerializer
    permission_classes = (
        ViewRepoPermission,
        ImportCoursePermission,
        IsAuthenticated,
    )

    def get_object(self):
        """
        Return details about a course in a repo
        """
        try:
            course = Course.objects.get(id=int(self.kwargs['course_id']))
        except (Course.DoesNotExist, ValueError):
            raise Http404()
        if course.repository.slug != self.kwargs['repo_slug']:
            raise Http404()
        return course

    @statsd.timer('lore.rest.course_detail_delete')
    def delete(self, request, *args, **kwargs):
        """
        Deletes a course in a repo with all the related learning resources and
        static assets
        """
        return super(CourseDetail, self).delete(request, *args, **kwargs)


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

    def update(self, request, *args, **kwargs):
        """
        Override to remove resource term links if resource type is
        removed. Note that partial_update will call this function too.
        """
        vocab = self.get_object()
        new_types = self.request.data.get('learning_resource_types', None)
        if new_types is not None:
            # Since LearningResourceTypes indicate which relationships
            # are valid between Terms and LearningResources, we need to
            # remove the newly invalid relationships caused by this update.
            old_types = set(
                t.name for t in vocab.learning_resource_types.all()
            )
            removed_types = old_types - set(new_types)

            resource_ids_to_reindex = []
            with transaction.atomic():
                for term in vocab.term_set.all():
                    for resource in term.learning_resources.all():
                        if (resource.learning_resource_type.name in
                                removed_types):
                            resource_ids_to_reindex.append(resource.id)
                            term.learning_resources.remove(resource)
            if len(resource_ids_to_reindex) > 0:
                index_resources.delay(resource_ids_to_reindex)

        return super(VocabularyDetail, self).update(
            request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Override delete to also update index for deleted vocabulary.
        """
        vocab = self.get_object()
        resource_ids = list(LearningResource.objects.filter(
            terms__vocabulary__id=vocab.id
        ).values_list("id", flat=True))
        ret = super(VocabularyDetail, self).delete(request, *args, **kwargs)
        index_resources.delay(resource_ids)
        return ret


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

    def delete(self, request, *args, **kwargs):
        """
        Override delete to also update index for deleted term.
        """
        term = self.get_object()
        resource_ids = list(LearningResource.objects.filter(
            terms__id=term.id
        ).values_list("id", flat=True))
        ret = super(TermDetail, self).delete(request, *args, **kwargs)
        index_resources.delay(resource_ids)
        return ret


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

        vocab_slug = self.request.query_params.get('vocab_slug', None)
        if vocab_slug is not None:
            queryset = queryset.filter(terms__vocabulary__slug=vocab_slug)

        type_names = self.request.query_params.getlist('type_name')
        if type_names:
            queryset = queryset.filter(
                learning_resource_type__name__in=type_names
            )
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

    def get(self, request, *args, **kwargs):
        """Override get to filter on content_xml."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        remove_content_xml = request.GET.get("remove_content_xml")
        if remove_content_xml == "true":
            data = dict(serializer.data)
            del data['content_xml']
        else:
            data = serializer.data
        return Response(data)

    def update(self, request, *args, **kwargs):
        """Override update to remove response."""
        super(LearningResourceDetail, self).update(request, *args, **kwargs)

        # Since content_xml may be large don't return the object
        # in the response unless user requests it via GET.
        return Response(status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to remove response."""
        super(LearningResourceDetail, self).partial_update(
            request, *args, **kwargs)

        # Since content_xml may be large don't return the object
        # in the response unless user requests it via GET.
        return Response(status=status.HTTP_200_OK)


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
            raise DjangoPermissionDenied()

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


class LearningResourceExportTaskList(ListCreateAPIView):
    """
    View for export tasks for a user. Deprecated! Use /api/v1/tasks/ instead.
    """
    serializer_class = LearningResourceExportTaskSerializer
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get export tasks for this user."""
        repo_slug = self.kwargs['repo_slug']
        export_tasks = [
            task for task in get_tasks(self.request.session).values()
            if task['task_type'] == EXPORT_TASK_TYPE and
            task['task_info']['repo_slug'] == repo_slug
        ]

        task_results = [create_task_result_dict(task) for task in export_tasks]

        return [
            {
                "id": result['id'],
                "status": result['status'],
                "url": result['result']['url'],
                "collision": result['result']['collision']
            } for result in task_results
        ]

    def post(self, request, *args, **kwargs):
        """
        Create a new export task for this user.

        Note that this also cancels and clears any old tasks for the user,
        so there should be only one task in the list at any time.

        The export list will be left alone. Once the list is exported
        the client may DELETE the export list as a separate REST call.
        """
        repo_slug = self.kwargs['repo_slug']
        export_tasks = [
            task for task in get_tasks(self.request.session).values()
            if task['task_type'] == EXPORT_TASK_TYPE and
            task['task_info']['repo_slug'] == repo_slug
        ]

        # Cancel any old tasks.
        for task in export_tasks:
            remove_task(self.request.session, task['id'])

        try:
            ids = self.request.data['ids']
        except KeyError:
            raise ValidationError("Missing ids")

        task = create_task(
            self.request.session,
            self.request.user.id,
            EXPORT_TASK_TYPE,
            {
                'repo_slug': repo_slug,
                'ids': ids
            }
        )

        return Response(
            {"id": task['id']},
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
        task_id = self.kwargs['task_id']
        initial_dict = get_task(self.request.session, task_id)
        if initial_dict is None:
            raise Http404

        result = create_task_result_dict(initial_dict)
        return {
            "id": result['id'],
            "status": result['status'],
            "url": result['result']['url'],
            "collision": result['result']['collision']
        }


class TaskList(ListCreateAPIView):
    """
    View for tasks for a user.
    """
    serializer_class = TaskSerializer
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        """Get tasks for this user."""
        tasks = get_tasks(self.request.session)

        return [create_task_result_dict(task) for task in tasks.values()]

    def post(self, request, *args, **kwargs):
        """
        Create a new task for this user.

        Note that this also cancels and clears any old tasks for the user,
        so there should be only one task in the list at any time.
        """

        if 'task_type' not in self.request.data:
            raise ValidationError("Missing task_type.")
        if 'task_info' not in self.request.data:
            raise ValidationError("Missing task_info.")

        try:
            result = create_task(
                self.request.session,
                self.request.user.id,
                self.request.data['task_type'],
                self.request.data['task_info']
            )
        except PermissionDenied:
            raise DjangoPermissionDenied
        except NotFound:
            raise Http404

        return Response(
            {"id": result['id']},
            status=status.HTTP_201_CREATED
        )


class TaskDetail(RetrieveDestroyAPIView):
    """
    Detail view for a user's tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = (
        IsAuthenticated,
    )

    def get_object(self):
        """
        Retrieve current information about a task.
        """
        task_id = self.kwargs['task_id']
        initial_dict = get_task(self.request.session, task_id)
        if initial_dict is None:
            raise Http404

        return create_task_result_dict(initial_dict)

    def delete(self, request, *args, **kwargs):
        """
        Remove task from list, revoke if necessary.
        """
        task_id = self.kwargs['task_id']
        remove_task(self.request.session, task_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


def calculate_selected_facets(selected_facet_params, facet_counts):
    """
    Given facet counts and the facet query parameters,
    return a dictionary of selected facets.
    """
    selected_facets = {}

    for counts in facet_counts.values():
        facet_id = counts['facet']['key']
        selected_facets[facet_id] = {}

        for value in counts['values']:
            value_id = value['key']
            param_value = "{facet}_exact:{value}".format(
                facet=facet_id,
                value=value_id
            )
            if param_value in selected_facet_params:
                selected_facets[facet_id][value_id] = True

    return selected_facets


def calculate_selected_missing_facets(selected_facet_params, facet_counts):
    """
    Given facet counts and the facet query parameters,
    return a dictionary of selected 'not tagged' facets.
    """
    selected_missing_facets = {}

    for counts in facet_counts.values():
        facet_id = counts['facet']['key']
        param = "_missing_:{facet}_exact".format(facet=facet_id)
        if param in selected_facet_params:
            selected_missing_facets[facet_id] = True

    return selected_missing_facets


class RepositorySearchList(GenericViewSet):
    """
    View of search results for repository search.
    """
    serializer_class = RepositorySearchSerializer
    permission_classes = (ViewRepoPermission, IsAuthenticated)

    def get_queryset(self):
        repo_slug = self.kwargs['repo_slug']
        query = self.request.GET.get('q', '')
        selected_facets = self.request.GET.getlist('selected_facets')
        sortby = self.request.GET.get('sortby', '')
        return construct_queryset(repo_slug, query, selected_facets, sortby)

    @statsd.timer('lore.rest.repository_search_list')
    def list(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Returns response object containing search results, including
        an extra value for facet_counts.
        """
        queryset = self.filter_queryset(self.get_queryset())
        facet_counts = queryset.aggregations()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        data = response.data
        data['facet_counts'] = facet_counts
        data['selected_facets'] = calculate_selected_facets(
            self.request.GET.getlist('selected_facets'),
            facet_counts
        )
        data['selected_missing_facets'] = calculate_selected_missing_facets(
            self.request.GET.getlist('selected_facets'),
            facet_counts
        )
        return Response(data)
