"""
Views for learningresources app.
"""

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from learningresources.api import get_repos
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
