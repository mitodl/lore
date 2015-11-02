# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F

from rest.util import default_slugify

# pylint: skip-file


def backfill_empty_slugs(apps, schema_editor):
    """
    Finds all the objects in the Repository
    that do not have a slug and change the name;
    this will automatically create a new slug.
    """
    Vocabulary = apps.get_model("taxonomy", "Vocabulary")
    Term = apps.get_model("taxonomy", "Term")

    for vocab in Vocabulary.objects.filter(slug=''):
        vocab.slug = default_slugify(
            vocab.name,
            Vocabulary._meta.model_name,
            lambda slug: Vocabulary.objects.filter(slug=slug).exists()
        )
        vocab.save()
    for term in Term.objects.filter(slug=''):
        term.slug = default_slugify(
            term.label,
            Term._meta.model_name,
            lambda slug: Term.objects.filter(slug=slug).exists()
        )
        term.save()


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0007_vocabulary_multi_terms'),
    ]

    operations = [
        migrations.RunPython(backfill_empty_slugs)
    ]
