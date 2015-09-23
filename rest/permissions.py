"""
Permission classes for REST views
"""

from __future__ import unicode_literals

from django.http import Http404
from guardian.shortcuts import get_perms
from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)

from learningresources.models import (
    Repository,
    LearningResource,
    StaticAsset,
)
from learningresources.api import (
    get_repo,
    PermissionDenied,
    NotFound,
)
from roles.permissions import RepoPermission
from taxonomy.api import (
    get_vocabulary,
    get_term,
)


# pylint: disable=protected-access
class AddRepoPermission(BasePermission):
    """checks add_repo permission"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            add_repo_permission = '{}.add_{}'.format(
                Repository._meta.app_label,
                Repository._meta.model_name
            )
            return request.user.has_perm(add_repo_permission)


class ViewRepoPermission(BasePermission):
    """Checks view_repo permission"""

    def has_permission(self, request, view):
        try:
            get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False
        return True


class ViewVocabularyPermission(BasePermission):
    """Checks view_repo permission on repository and that
    repository owns vocabulary"""

    def has_permission(self, request, view):
        try:
            get_vocabulary(
                view.kwargs['repo_slug'],
                request.user.id,
                view.kwargs['vocab_slug']
            )
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False
        return True


class ViewTermPermission(BasePermission):
    """Checks view_repo permission on repository and that repository owns
    vocabulary and that vocabulary owns term"""

    def has_permission(self, request, view):
        try:
            get_term(
                view.kwargs['repo_slug'],
                request.user.id,
                view.kwargs['vocab_slug'],
                view.kwargs['term_slug']
            )
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False
        return True


class ManageTaxonomyPermission(BasePermission):
    """Checks manage_taxonomy permission"""

    def has_permission(self, request, view):
        # verify repo just in case we haven't done this earlier
        try:
            get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False

        if request.method in SAFE_METHODS:
            return True
        else:
            repo_slug = view.kwargs['repo_slug']
            try:
                repo = Repository.objects.get(slug=repo_slug)
            except Repository.DoesNotExist:
                raise NotFound()

            return (
                RepoPermission.manage_taxonomy[0]
                in get_perms(request.user, repo)
            )


class ManageRepoMembersPermission(BasePermission):
    """Checks manage_repo_users permission"""

    def has_permission(self, request, view):
        try:
            repo = get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()  # pragma: no cover
        except PermissionDenied:
            return False
        if request.method in SAFE_METHODS:
            return True
        return RepoPermission.manage_repo_users[0] in get_perms(
            request.user, repo)


class AddEditMetadataPermission(BasePermission):
    """Checks add_edit_metadata permission"""

    def has_permission(self, request, view):
        try:
            repo = get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False

        if request.method in SAFE_METHODS:
            return True

        return (
            RepoPermission.add_edit_metadata[0]
            in get_perms(request.user, repo)
        )


class ViewLearningResourcePermission(ViewRepoPermission):
    """
    Checks that user has view_repo permission for the repository
    and that that repo owns the LearningResource being requested.
    """

    def has_permission(self, request, view):
        if not super(ViewLearningResourcePermission, self).has_permission(
                request, view):
            return False

        repo_slug = view.kwargs['repo_slug']
        lr_id = int(view.kwargs['lr_id'])

        try:
            LearningResource.objects.filter(
                course__repository__slug=repo_slug).get(id=lr_id)
        except LearningResource.DoesNotExist:
            raise Http404()

        return True


class ViewStaticAssetPermission(ViewLearningResourcePermission):
    """
    Checks that user has view_repo permission for the repository
    and that that repo owns the LearningResource being requested.
    """

    def has_permission(self, request, view):
        if not super(ViewStaticAssetPermission, self).has_permission(
                request, view):
            return False

        lr_id = int(view.kwargs['lr_id'])
        sa_id = int(view.kwargs['sa_id'])

        try:
            StaticAsset.objects.filter(
                learningresource__id=lr_id).get(id=sa_id)
        except StaticAsset.DoesNotExist:
            raise Http404()

        return True


class ViewLearningResourceExportPermission(BasePermission):
    """
    Checks that username mentioned is the same one as the request.
    In the future we may want to let users see each other's exports
    but for now this just enforces the user seeing their own exports.
    """

    def has_permission(self, request, view):
        username = view.kwargs['username']

        return request.user.username == username


class ImportCoursePermission(BasePermission):
    """
    Checks that the user has permission to import a course.
    The same permission is used to check if the user can delete a course.
    """
    def has_permission(self, request, view):
        try:
            repo = get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False
        if request.method in SAFE_METHODS:
            return True
        return RepoPermission.import_course[0] in get_perms(request.user, repo)
