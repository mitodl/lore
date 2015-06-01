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
from .forms import UploadForm

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
def upload(request, repo_id):
    """
    Upload a OLX archive.
    """
    if int(repo_id) not in set([x.id for x in get_repos(request.user.id)]):
        return HttpResponseForbidden("unauthorized")
    form = UploadForm()
    message = ""
    if request.method == "POST":
        form = UploadForm(
            data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                form.save(request.user, repo_id)
                return redirect("/lore/listing/{0}/1".format(repo_id))
            except ValueError as ex:
                log.debug("ex args: %s", ex.args)
                if "Duplicate course" not in ex.args:
                    raise ex
                message = "Duplicate course"
    return render(
        request,
        "upload.html",
        {'form': form, "message": message, "repo_id": repo_id},
    )
