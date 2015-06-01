"""
Views for the taxonomy app
"""
from __future__ import unicode_literals

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from .forms import VocabularyForm
from learningresources.models import Repository
from taxonomy.models import Vocabulary


def create_vocabulary(request, repository_id):
    """
    Show form to create a new vocabulary
    """
    form = VocabularyForm()

    repository = get_object_or_404(Repository, id=repository_id)

    if request.method == "POST":
        form = VocabularyForm(request.POST)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'taxonomy:edit_vocabulary',
                vocabulary_id=form.instance.id,
                repository_id=repository_id,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'repository_id': repository_id,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'repository_id': repository_id,
        }
    )


def edit_vocabulary(request, repository_id, vocabulary_id):
    """
    Show form to edit an existing vocabulary
    """
    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    form = VocabularyForm(instance=vocabulary)

    repository = get_object_or_404(Repository, id=repository_id)
    form.instance.repository = repository
    form.instance.required = False
    form.instance.weight = 1000

    if request.method == "POST":
        form = VocabularyForm(request.POST)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'taxonomy:edit_vocabulary',
                vocabulary_id=form.instance.id,
                repository_id=repository_id,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'vocabulary_id': vocabulary_id,
                'repository_id': repository_id,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'vocabulary_id': vocabulary_id,
            'repository_id': repository_id,
        }
    )
