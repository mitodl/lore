# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0011_learningresource_url_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningresource',
            name='description_path',
            field=models.TextField(blank=True),
        ),
    ]
