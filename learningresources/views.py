"""
Views for learningresources app.
"""

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from learningresources.api import get_repos, get_courses
from learningresources.forms import RepositoryForm


@login_required
def welcome(request):
    """
    Greet the user, show available repositories.
    """
    return render(
        request,
        "welcome.html",
        {"repos": get_repos(request.user)}
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
    if int(repo_id) not in set([x.id for x in get_repos(request.user)]):
        return HttpResponseForbidden("unauthorized")
    context = {
        "repo": repo_id,
        "courses": get_courses(repo_id),
    }
    return render(
        request,
        "listing.html",
        context,
    )
