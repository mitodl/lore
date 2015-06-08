"""
Views for the importer app.
"""

from __future__ import unicode_literals

import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseForbidden

from learningresources.models import Repository, Course, LearningResource
from learningresources.api import get_repos
from ui.forms import UploadForm

log = logging.getLogger(__name__)


def status(request):
    """
    Show what's currently in the system.
    """
    counts = {
        "repos": Repository.objects.count(),
        "courses": Course.objects.count(),
        "resources": LearningResource.objects.count(),
    }
    return render(
        request,
        "status.html",
        counts,
    )


@login_required
def upload(request, repo_slug):
    """
    Upload a OLX archive.
    """
    if repo_slug not in set([x.slug for x in get_repos(request.user.id)]):
        return HttpResponseForbidden("unauthorized")
    repo = [x for x in get_repos(request.user.id) if x.slug == repo_slug][0]
    form = UploadForm()
    if request.method == "POST":
        form = UploadForm(
            data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(request.user.id, repo.id)
            return redirect("/repositories/{0}/".format(repo_slug))
    return render(
        request,
        "upload.html",
        {'form': form, "repo": repo},
    )
