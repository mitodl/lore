"""
Views for learningresources app.
"""

import logging

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from learningresources.api import (
    get_repos, get_repo_courses, get_semesters, get_user_tags
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
def listing(request, repo_id):
    """
    View available LearningResources by repository.
    """
    # Enforce repository access restrictions.
    log.debug("in listing view")
    if int(repo_id) not in set([x.id for x in get_repos(request.user.id)]):
        return HttpResponseForbidden("unauthorized")
    context = {
        "repo": repo_id,
        "courses": get_repo_courses(repo_id),
        "semesters": get_semesters(request.user.id),
        "tags": get_user_tags(request.user.id),
    }
    log.debug("%s tags", context["tags"].count())
    return render(
        request,
        "listing.html",
        context,
    )
