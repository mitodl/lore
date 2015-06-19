# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0003_populate_slug_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='slug',
            field=models.CharField(unique=True, max_length=256),
            preserve_default=False,
        ),
    ]
