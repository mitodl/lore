# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# pylint: skip-file
class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='label',
            field=models.CharField(max_length=256),
        ),
        migrations.AddField(
            model_name='term',
            name='slug',
            field=models.CharField(null=True, max_length=256),
            preserve_default=False,
        ),
    ]
