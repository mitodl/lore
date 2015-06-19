"""
Permission classes for REST views
"""

from __future__ import unicode_literals

from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)
from django.http import Http404

from learningresources.models import Repository
from learningresources.api import (
    get_repo,
    PermissionDenied,
    NotFound,
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
