# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from learningresources.api import update_description_path

# pylint: skip-file


def update_description_paths(apps, schema_editor):
    """update the description path field"""
    LearningResource = apps.get_model("learningresources", "LearningResource")
    for learning_resource in LearningResource.objects.all():  # pragma: no cover
        if learning_resource.title == "Getting Started":
            learning_resource.title = "..."
            learning_resource.save()
            update_description_path(learning_resource, force_parent_update=True)  # pragma: no cover


class Migration(migrations.Migration):

    dependencies = [
        (
            'learningresources',
            '0016_revert_backfill'
        ),
    ]

    operations = [
        migrations.RunPython(update_description_paths)
    ]
