# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F

from learningresources.api import update_description_path, MissingTitle

# pylint: skip-file


def replace_missing_title(apps, schema_editor):
    """
    Replaces `MISSING` with `Missing Title` in the title field
    and with `...` in the description_path field
    """
    # replace title
    new_title = 'Missing Title'
    LearningResource = apps.get_model("learningresources", "LearningResource")
    # update description path
    for learning_resource in LearningResource.objects.all().order_by('id'):
        if learning_resource.title == 'MISSING':
            learning_resource.title = new_title
            learning_resource.save()
        update_description_path(learning_resource)


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0016_revert_backfill'),
    ]

    operations = [
        migrations.RunPython(replace_missing_title)
    ]
