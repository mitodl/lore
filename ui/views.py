"""
Views for the all apps
"""
from __future__ import unicode_literals

import logging
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from haystack.views import FacetedSearchView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms

from learningresources.api import (
    get_repo, get_repos, get_resource, NotFound,
)
from learningresources.models import Repository, StaticAsset
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes, RepoPermission
from search import get_sqs
from taxonomy.models import Vocabulary
from ui.forms import UploadForm, RepositoryForm

log = logging.getLogger(__name__)


@login_required
@permission_required_or_403(
    # pylint: disable=protected-access
    # the following string is "learningresources.import_course"
    # (unless the Repository model has been moved)
    '{}.{}'.format(
        Repository._meta.app_label,
        RepoPermission.import_course[0]
    ),
    (Repository, 'slug', 'repo_slug')
)
def upload(request, repo_slug):
    """
    Upload a OLX archive.
    """
    repo = get_repo(repo_slug, request.user.id)
    form = UploadForm()
    if request.method == "POST":
        form = UploadForm(
            data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                form.save(request.user.id, repo.id)
                return redirect("/repositories/{0}/".format(repo_slug))
            except ValueError as ex:
                # Coverage exception reasoning: After successful upload,
                # extraction, and validation, any error *should* be
                # "Duplicate course," and if it's not, it will be re-raised
                # and we'll code for it then.
                if "Duplicate course" not in ex.args:  # pragma: no cover
                    raise ex
                form.add_error("course_file", "Duplicate course")
    return render(
        request,
        "upload.html",
        {'form': form, "repo": repo},
    )


@login_required
def welcome(request):
    """
    Greet the user, show available repositories.
    """
    return render(
        request,
        "welcome.html",
        {
            "repos": get_repos(request.user.id),
            "support_email": settings.EMAIL_SUPPORT,
        }
    )


@login_required
@permission_required_or_403(
    # pylint: disable=protected-access
    # the following string is "learningresources.add_repo"
    # (unless the Repository model has been moved)
    '{}.add_{}'.format(
        Repository._meta.app_label,
        Repository._meta.model_name
    )
)
def create_repo(request):
    """
    Create a new repository.
    """
    form = RepositoryForm()
    if request.method == "POST":
        form = RepositoryForm(data=request.POST)
        if form.is_valid():
            repo = form.save(request.user)
            assign_user_to_repo_group(
                request.user,
                repo,
                GroupTypes.REPO_ADMINISTRATOR
            )
            return redirect(reverse("repositories", args=(repo.slug,)))
    return render(
        request,
        "create_repo.html",
        {"form": form},
    )


class RepositoryView(FacetedSearchView):
    """Subclass of haystack.views.FacetedSearchView"""

    # pylint: disable=arguments-differ
    # We need the extra kwarg.
    def __call__(self, request, repo_slug):
        # Get arguments from the URL
        # pylint: disable=attribute-defined-outside-init
        # It's a subclass of an external class, so we don't have
        # repo_slug in __init__.
        repos = get_repos(request.user.id)
        if repo_slug not in set([x.slug for x in repos]):
            return HttpResponseForbidden("unauthorized")
        self.repo = [x for x in repos if x.slug == repo_slug][0]
        return super(RepositoryView, self).__call__(request)

    def dispatch(self, *args, **kwargs):
        """Override for the purpose of having decorators in views.py"""
        super(RepositoryView, self).dispatch(*args, **kwargs)

    def extra_context(self):
        """Add to the context."""
        context = super(RepositoryView, self).extra_context()
        vocabularies = Vocabulary.objects.all().values_list("slug", "name")
        params = dict(self.request.GET.copy())
        qs_prefix = "?"
        # Chop out page number so we don't end up with
        # something like ?page=2&page=3&page=4.
        if "page" in params:
            params.pop("page")
        if len(params) > 0:
            qs_prefix = []
            for key in params.keys():
                qs_prefix.append(
                    "&".join([
                        "{0}={1}".format(key, val)
                        for val in params[key]
                    ])
                )
            qs_prefix = "?{0}&".format("&".join(qs_prefix))

        if "fields" in context["facets"]:
            _vocabularies = []
            for slug, facet in context["facets"]["fields"].items():
                for vocabulary in vocabularies:
                    if vocabulary[0] == slug:
                        _vocabularies.append((slug, vocabulary[1], facet))
            context.update({
                "repo": self.repo,
                "perms_on_cur_repo": get_perms(self.request.user, self.repo),
                "vocabularies": _vocabularies,
                "qs_prefix": qs_prefix,
            })
        return context

    def build_form(self, form_kwargs=None):
        """Override of FacetedSearchView.build_form to inject repo slug."""
        # get_sqs must be called here instead of putting it in urls.py as
        # would be the default. This is because vocabularies could be added
        # by the user at runtime, and we need to be able to search on those
        # facets without restarting Django.
        self.searchqueryset = get_sqs()
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs["repo_slug"] = self.repo.slug
        return super(RepositoryView, self).build_form(form_kwargs)


# pylint: disable=unused-argument
# repo_slug argument will be used by the decorator to protect the view
@login_required
@permission_required_or_403(
    # pylint: disable=protected-access
    # the following string is "learningresources.import_course"
    # (unless the Repository model has been moved)
    '{}.{}'.format(
        Repository._meta.app_label,
        RepoPermission.view_repo[0]
    ),
    (Repository, 'slug', 'repo_slug')
)
def export(request, repo_slug, resource_id):
    """Dump LearningResource as XML"""
    try:
        return HttpResponse(
            get_resource(resource_id, request.user.id).content_xml,
            content_type='text/xml'
        )
    except NotFound:
        raise Http404()


@login_required
def serve_media(request, media_path):
    """
    View to serve media files in case settings.DEFAULT_FILE_STORAGE
    is django.core.files.storage.FileSystemStorage
    """
    # first check if the user has access to the file
    file_path = os.path.join(settings.MEDIA_ROOT, media_path)
    static_asset = get_object_or_404(StaticAsset, asset=media_path)
    if (RepoPermission.view_repo[0] not in
            get_perms(request.user, static_asset.course.repository)):
        raise PermissionDenied()
    filename = os.path.basename(file_path)
    response = StreamingHttpResponse(
        FileWrapper(open(file_path)),
        content_type=mimetypes.guess_type(file_path)[0]
    )
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
