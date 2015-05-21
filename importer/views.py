"""
Views for the importer app.
"""

from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import transaction

from learningresources.models import Repository, Course, LearningResource
from .forms import UploadForm


def status(request):
    """
    Show what's currently in the system.
    """
    counts = {
        "repos": Repository.objects.count(),
        "courses": Course.objects.count(),
        "loxes": LearningResource.objects.count(),
    }
    return render(
        request,
        "status.html",
        counts,
    )


def upload(request):
    """
    Upload a OLX archive.
    """
    form = UploadForm()
    if request.user.is_anonymous():
        with transaction.atomic():
            request.user, _ = User.objects.get_or_create(username="dirty_hack")
    if request.method == "POST":
        form = UploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(request.user)
    return render(
        request,
        "upload.html",
        {'form': form},
    )
