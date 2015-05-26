"""
Views for the importer app.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from learningresources.models import Repository, Course, LearningResource
from .forms import UploadForm


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
def upload(request):
    """
    Upload a OLX archive.
    """
    form = UploadForm()
    if request.method == "POST":
        form = UploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(request.user)
    return render(
        request,
        "upload.html",
        {'form': form},
    )
