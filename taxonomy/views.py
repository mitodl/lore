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


def create_vocabulary(request, repo_slug):
    """
    Show form to create a new vocabulary
    """
    form = VocabularyForm()

    repository = get_object_or_404(Repository, slug=repo_slug)

    if request.method == "POST":
        form = VocabularyForm(request.POST)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'edit_vocabulary',
                vocab_slug=form.instance.slug,
                repo_slug=repo_slug,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'repo_slug': repo_slug,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'repo_slug': repo_slug,
        }
    )


def edit_vocabulary(request, repo_slug, vocab_slug):
    """
    Show form to edit an existing vocabulary
    """
    vocabulary = get_object_or_404(Vocabulary, slug=vocab_slug)
    form = VocabularyForm(instance=vocabulary)

    repository = get_object_or_404(Repository, slug=repo_slug)
    form.instance.repository = repository
    form.instance.required = False
    form.instance.weight = 1000

    if request.method == "POST":
        form = VocabularyForm(request.POST, instance=vocabulary)

        form.instance.repository = repository
        form.instance.required = False
        form.instance.weight = 1000
        if form.is_valid():
            form.save()
            return redirect(
                'edit_vocabulary',
                vocab_slug=form.instance.slug,
                repo_slug=repo_slug,
            )

        return render(
            request,
            "vocabulary.html",
            {
                'form': form,
                'vocab_slug': vocab_slug,
                'repo_slug': repo_slug,
            }
        )

    return render(
        request,
        "vocabulary.html",
        {
            'form': form,
            'vocab_slug': vocab_slug,
            'repo_slug': repo_slug,
        }
    )
