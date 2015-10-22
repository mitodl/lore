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
    Repository = apps.get_model("learningresources", "Repository")

    for repo in Repository.objects.filter(slug=''):
        repo.slug = default_slugify(
            repo.name,
            Repository._meta.model_name,
            lambda slug: Repository.objects.filter(slug=slug).exists()
        )
        repo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0017_learningresource_missing_title_update'),
    ]

    operations = [
        migrations.RunPython(backfill_empty_slugs)
    ]
