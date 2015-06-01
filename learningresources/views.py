"""
Views for learningresources app.
"""

import logging

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from learningresources.api import (
    get_repos, get_repo_courses, get_runs, get_user_tags,
    get_user_resources,
)
from learningresources.forms import RepositoryForm

log = logging.getLogger(__name__)


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
def create_repo(request):
    """
    Create a new repository.
    """
    form = RepositoryForm()
    if request.method == "POST":
        form = RepositoryForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect(reverse("welcome"))
    return render(
        request,
        "create_repo.html",
        {"form": form},
    )


@login_required
def listing(request, repo_id, page=1):
    """
    View available LearningResources by repository.
    """
    # Enforce repository access restrictions.
    repo_id = int(repo_id)
    repos = get_repos(request.user.id)
    if repo_id not in set([x.id for x in repos]):
        return HttpResponseForbidden("unauthorized")
    repo = [x for x in repos if x.id == repo_id][0]
    context = {
        "repo_id": repo_id,
        "repo": repo,
        "courses": get_repo_courses(repo_id),
        "runs": get_runs(repo_id, request.user.id),
        "tags": get_user_tags(repo_id, request.user.id),
        "resources": Paginator(
            get_user_resources(repo_id, request.user.id), 20).page(page)
    }
    log.debug("%s tags", context["tags"].count())
    return render(
        request,
        "listing.html",
        context,
    )
