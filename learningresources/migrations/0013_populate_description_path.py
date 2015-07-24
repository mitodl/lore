# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F

from learningresources.api import update_description_path

# pylint: skip-file


def populate_description_paths(apps, schema_editor):
    """Populate the description path field"""
    LearningResource = apps.get_model("learningresources", "LearningResource")
    for learning_resource in LearningResource.objects.all():  # pragma: no cover
        update_description_path(learning_resource)  # pragma: no cover


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0012_learningresource_description_path'),
    ]

    operations = [
        migrations.RunPython(populate_description_paths)
    ]
