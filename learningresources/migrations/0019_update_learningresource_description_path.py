# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F

from learningresources.api import update_description_path

# pylint: skip-file


def update_description_paths(apps, schema_editor):
    """update the description path field"""
    LearningResource = apps.get_model("learningresources", "LearningResource")
    for learning_resource in LearningResource.objects.all():  # pragma: no cover
        description_path = (
            learning_resource.description_path.replace("edX Demonstration Course", "...")
        )
        learning_resource.description_path = description_path
        learning_resource.save()
        print(learning_resource)
        update_description_path(learning_resource)  # pragma: no cover


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0018_update_learningresource_description_path'),
    ]

    operations = [
        migrations.RunPython(update_description_paths)
    ]
