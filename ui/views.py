"""
Views for the all apps
"""
from __future__ import unicode_literals

import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from haystack.views import SearchView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_perms

from learningresources.api import (
    get_repo_courses, get_repo_or_error, get_repos,
    get_resource, get_runs, get_user_tags,
)
from learningresources.models import Repository
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes, RepoPermission
from taxonomy.models import Vocabulary
from ui.forms import UploadForm, VocabularyForm, RepositoryForm

log = logging.getLogger(__name__)


@login_required
def create_vocabulary(request, repo_slug):
    """
    Show form to create a new vocabulary
    """
    form = VocabularyForm()

    repository = get_object_or_404(Repository, slug=repo_slug)

    if request.method == "POST":
        form = VocabularyForm(request.POST)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'edit_vocabulary',
                vocab_slug=form.instance.slug,
                repo_slug=repo_slug,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'repo_slug': repo_slug,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'repo_slug': repo_slug,
        }
    )


@login_required
def edit_vocabulary(request, repo_slug, vocab_slug):
    """
    Show form to edit an existing vocabulary
    """
    vocabulary = get_object_or_404(Vocabulary, slug=vocab_slug)
    form = VocabularyForm(instance=vocabulary)

    repository = get_object_or_404(Repository, slug=repo_slug)
    form.instance.repository = repository
    form.instance.required = False
    form.instance.weight = 1000

    if request.method == "POST":
        form = VocabularyForm(request.POST, instance=vocabulary)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'edit_vocabulary',
                vocab_slug=form.instance.slug,
                repo_slug=repo_slug,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'vocab_slug': vocab_slug,
                'repo_slug': repo_slug,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'vocab_slug': vocab_slug,
            'repo_slug': repo_slug,
        }
    )


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
    repo = get_repo_or_error(repo_slug, request.user.id)
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
        {"repos": get_repos(request.user.id)}
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


class RepositoryView(SearchView):
    """Subclass of haystack.views.SearchView"""

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

    @login_required
    def dispatch(self, *args, **kwargs):
        """Override for the purpose of having decorators in views.py"""
        super(RepositoryView, self).dispatch(*args, **kwargs)

    def extra_context(self):
        """Add to the context."""
        context = {
            "repo": self.repo,
            "courses": get_repo_courses(self.repo.id),
            "runs": get_runs(self.repo.id),
            "tags": get_user_tags(self.repo.id),
            "perms_on_cur_repo": get_perms(self.request.user, self.repo)
        }
        return context


@login_required
def export(request, resource_id):
    """Dump LearningResource as XML"""
    return HttpResponse(
        get_resource(resource_id, request.user.id).content_xml,
        content_type='text/xml'
    )
