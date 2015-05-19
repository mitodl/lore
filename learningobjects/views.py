"""
Views for learningobjects app.
"""

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from learningobjects.api import get_repos
from learningobjects.forms import RepositoryForm


def welcome(request):
    """
    Greet the user, show available repositories.
    """
    return render(
        request,
        "learningobjects/welcome.html",
        {"repos": get_repos(request.user)}
    )


def create_repo(request):
    """
    Create a new repository.
    """
    form = RepositoryForm()
    if request.method == "POST":
        request.user, _ = User.objects.get_or_create(username="dirty_hack")
        form = RepositoryForm(data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect(reverse("welcome"))
    return render(
        request,
        "learningobjects/create_repo.html",
        {"form": form},
    )
