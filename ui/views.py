"""
Views for the all apps
"""
from __future__ import unicode_literals

import logging
import mimetypes
import json
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from haystack.views import FacetedSearchView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms
from statsd.defaults.django import statsd

from learningresources.api import (
    get_repo,
    get_repos,
    NotFound,
    PermissionDenied as LorePermissionDenied,
)
from learningresources.models import (
    LearningResource,
    Repository,
    LearningResource,
    StaticAsset,
    STATIC_ASSET_PREFIX,
)
from roles.permissions import RepoPermission
from search import get_sqs
from search.sorting import LoreSortingFields
from taxonomy.models import Vocabulary, Term
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
            return redirect(reverse("repositories", args=(repo.slug,)))
    return render(
        request,
        "create_repo.html",
        {"form": form},
    )


def get_vocabularies(facets):
    """
    Parse facet information for the template.
    It will return a dictionary that looks like this:

    {
        (u'13', u'difficulty'): [(38, u'medium', 23), (17, u'hard', 19)],
        (u'15', u'prerequisite'): [(44, u'yes', 23)]
    }

    The keys are tuples with Vocabulary ID and name for the key,
    and a list of tuples containing id, label, and count for the terms.

    This is for ease-of-use in the template, where the integer primary keys
    are used for search links and the names/labels are used for display.

    Args:
        facets (dict): facet ID with terms & term counts
    Returns:
        vocabularies (dict): dict of vocab info to term info
    """

    if "fields" not in facets:
        return {}
    vocab_ids = []
    term_ids = []
    for vocab_id, counts in facets["fields"].items():
        if not vocab_id.isdigit():
            continue
        vocab_ids.append(int(vocab_id))
        for term_id, count in counts:
            term_ids.append(term_id)

    vocabs = {
        x: y for x, y in Vocabulary.objects.filter(
            id__in=vocab_ids).values_list('id', 'name')
    }
    terms = {
        x: y for x, y in Term.objects.filter(
            id__in=term_ids).values_list('id', 'label')
    }
    vocabularies = {}
    for vocabulary_id, term_data in facets["fields"].items():
        if not vocabulary_id.isdigit():
            continue
        vocab = (vocabulary_id, vocabs[int(vocabulary_id)])
        vocabularies[vocab] = []
        notset = None
        for t_id, count in term_data:
            # Save this for last if it exists.
            if terms[int(t_id)] == Term.EMPTY_VALUE:
                notset = (t_id, terms[int(t_id)], count)
            else:
                vocabularies[vocab].append((t_id, terms[int(t_id)], count))
        # By default, sort alphabetically.
        vocabularies[vocab].sort(key=lambda x: x[1])
        # Add "not set" value after alphabetized values.
        if notset is not None:
            vocabularies[vocab].append(notset)
    return vocabularies


class RepositoryView(FacetedSearchView):
    """Subclass of haystack.views.FacetedSearchView."""

    # pylint: disable=arguments-differ
    # We need the extra kwarg.
    @statsd.timer('lore.repository_view')
    def __call__(self, request, repo_slug):
        # Get arguments from the URL
        # It's a subclass of an external class, so we don't have
        # repo_slug in __init__.
        # pylint: disable=attribute-defined-outside-init
        try:
            self.repo = get_repo(repo_slug, request.user.id)
        except NotFound:
            raise Http404()
        except LorePermissionDenied:
            raise PermissionDenied('unauthorized')
        # get sorting from params if it's there
        sortby = dict(request.GET.copy()).get('sortby', [])
        if (len(sortby) > 0 and
                sortby[0] in LoreSortingFields.all_sorting_fields()):
            self.sortby = sortby[0]
        else:
            # default value
            self.sortby = LoreSortingFields.DEFAULT_SORTING_FIELD
        return super(RepositoryView, self).__call__(request)

    def dispatch(self, *args, **kwargs):
        """Override for the purpose of having decorators in views.py."""
        super(RepositoryView, self).dispatch(*args, **kwargs)

    def extra_context(self):
        """Add to the context."""
        context = super(RepositoryView, self).extra_context()
        params = dict(self.request.GET.copy())
        qs_prefix = "?"
        # Chop out page number so we don't end up with
        # something like ?page=2&page=3&page=4.
        if "page" in params:
            params.pop("page")
        # for the same reason I remove the sorting
        if "sortby" in params:
            params.pop("sortby")
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

        def make_dict(result):
            """Serialize result to dict."""
            return {
                "lid": result.lid,
                "resource_type": result.resource_type,
                "title": result.title,
                "course": result.course,
                "run": result.run,
                "description": result.description,
                "description_path": result.description_path,
                "preview_url": result.preview_url,
                "xa_nr_views": result.nr_views,
                "xa_nr_attempts": result.nr_attempts,
                "xa_avg_grade": result.avg_grade,
            }

        page_no = int(self.request.GET.get('page', 1))
        page = self.build_page()[0].page(page_no)

        # Provide information used to populate listing UI.
        resources = [make_dict(result) for result in page]
        exports = self.request.session.get(
            'learning_resource_exports', {}).get(self.repo.slug, [])
        show_export_button = LearningResource.objects.filter(
            course__repository__id=self.repo.id
        ).exists()

        sorting_options = {
            "current": LoreSortingFields.get_sorting_option(
                self.sortby),
            "all": LoreSortingFields.all_sorting_options_but(
                self.sortby)
        }

        context.update({
            "repo": self.repo,
            "perms_on_cur_repo": get_perms(self.request.user, self.repo),
            "vocabularies": get_vocabularies(context["facets"]),
            "qs_prefix": qs_prefix,
            "sorting_options": sorting_options,
            "sorting_options_json": json.dumps(sorting_options),
            "resources_json": json.dumps(resources),
            "exports_json": json.dumps(exports),
            "show_export_button_json": json.dumps(show_export_button)
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
        form_kwargs["sortby"] = self.sortby
        return super(RepositoryView, self).build_form(form_kwargs)


@login_required
def serve_static_assets(request, path):
    """
    View to serve media files in case settings.DEFAULT_FILE_STORAGE
    is django.core.files.storage.FileSystemStorage
    """
    # first check if the user has access to the file
    media_path = os.path.join(STATIC_ASSET_PREFIX, path)
    file_path = os.path.join(settings.MEDIA_ROOT, media_path)
    static_asset = get_object_or_404(StaticAsset, asset=media_path)
    if (RepoPermission.view_repo[0] not in
            get_perms(request.user, static_asset.course.repository)):
        raise PermissionDenied()
    filename = os.path.basename(file_path)
    response = StreamingHttpResponse(
        FileWrapper(open(file_path, 'rb')),
        content_type=mimetypes.guess_type(file_path)[0]
    )
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@login_required
def serve_resource_exports(request, path):
    """
    View to serve media files in case settings.DEFAULT_FILE_STORAGE
    is django.core.files.storage.FileSystemStorage
    """
    media_path = os.path.join(settings.EXPORT_PATH_PREFIX, path)
    file_path = os.path.join(settings.MEDIA_ROOT, media_path)

    # There is only one path that will work here, make sure it matches exactly.
    expected_filename = "{name}_exports.tar.gz".format(
        name=request.user.username
    )
    expected_path = os.path.join(
        settings.MEDIA_ROOT, settings.EXPORT_PATH_PREFIX, expected_filename)
    if expected_path != file_path:
        raise PermissionDenied()
    if not os.path.exists(file_path):
        raise Http404()

    filename = os.path.basename(file_path)
    response = StreamingHttpResponse(
        FileWrapper(open(file_path, 'rb')),
        content_type=mimetypes.guess_type(file_path)[0]
    )
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename={filename}".format(
        filename=filename
    )
    return response
