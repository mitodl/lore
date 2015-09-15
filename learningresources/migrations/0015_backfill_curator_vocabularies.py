# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify

# pylint: skip-file

VOCAB_NAME = "curation status"
EMPTY_VALUE = "--not set--"


def backfill_curator_vocabs(apps, schema_editor):
    """Backfill auto-generated vocabulary to existing repos."""
    Repository = apps.get_model("learningresources", "Repository")
    LearningResourceType = apps.get_model(
        "learningresources", "LearningResourceType")
    Vocabulary = apps.get_model("taxonomy", "Vocabulary")
    learning_resource_types = LearningResourceType.objects.all()
    for repo in Repository.objects.all().iterator():
        if Vocabulary.objects.filter(
            name=VOCAB_NAME, repository__id=repo.id).exists():
            continue
        vocab = Vocabulary.objects.create(
            repository_id=repo.id,
            name=VOCAB_NAME, description=VOCAB_NAME,
            required=True, vocabulary_type='m',
            weight=0, multi_terms=False,
            slug=slugify("{0}_{1}_backfill".format(VOCAB_NAME, repo.id)),
        )
        for resource_type in learning_resource_types:
            vocab.learning_resource_types.add(resource_type)
        create_terms(apps, vocab.id)
        backfill_resources(apps, repo.id)


def create_terms(apps, vocab_id):
    """Create the curation status terms for a newly-created Vocabulary."""
    Term = apps.get_model("taxonomy", "Term")
    labels = (
        'ready to use', 'tagged', 'course information',
        'discarded', 'hidden', EMPTY_VALUE,
    )
    for label in labels:
        Term.objects.create(
            vocabulary_id=vocab_id,
            label=label,
            slug=slugify("{0}_{1}_backfill".format(label, vocab_id)),
            weight=0,
        )


def backfill_resources(apps, repo_id):
    """Add terms to existing LearningResource instances."""
    LearningResource = apps.get_model("learningresources", "LearningResource")
    Term = apps.get_model("taxonomy", "Term")
    empty_term = Term.objects.get(
        vocabulary__repository__id=repo_id,
        vocabulary__name=VOCAB_NAME,
        label=EMPTY_VALUE,
    )
    resources = LearningResource.objects.filter(
        course__repository__id=repo_id
    )
    ThroughModel = Term.learning_resources.through

    to_insert = [
        ThroughModel(
            learningresource_id=resource.id,
            term_id=empty_term.id,
        ) for resource in resources.all()
    ]

    ThroughModel.objects.bulk_create(to_insert)


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0014_learning_resource_related_name'),
        ('taxonomy', '0007_vocabulary_multi_terms'),
    ]

    operations = [
        migrations.RunPython(backfill_curator_vocabs)
    ]
