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

from learningresources.models import Repository
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
        if request.method in SAFE_METHODS:
            return True
        try:
            repo = get_repo(view.kwargs['repo_slug'], request.user.id)
        except NotFound:
            raise Http404()
        except PermissionDenied:
            return False
        return RepoPermission.manage_repo_users[0] in get_perms(
            request.user, repo)
