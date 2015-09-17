# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import unicodedata

# pylint: skip-file


def update_description_paths(apps, schema_editor):
    """update the description path field"""
    LearningResource = apps.get_model("learningresources", "LearningResource")
    for learning_resource in LearningResource.objects.all():  # pragma: no cover
        current_description_path = learning_resource.description_path
        replace_sub_str = u"edX Demonstration Course"
        replacement_sub_str = u"..."

        new_description_path = (
            current_description_path.replace(
                replace_sub_str, replacement_sub_str
            )
        )
        learning_resource.description_path = new_description_path
        learning_resource.save()


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0021_update_learningresource_description_path'),
    ]

    operations = [
        migrations.RunPython(update_description_paths)
    ]
