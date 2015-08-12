# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0013_populate_description_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningresource',
            name='course',
            field=models.ForeignKey(related_name='resources', to='learningresources.Course'),
        ),
    ]
