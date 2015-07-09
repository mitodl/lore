# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0008_remove_staticasset_learning_resources'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningresource',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
