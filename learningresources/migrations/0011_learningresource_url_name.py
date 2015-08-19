# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0010_static_asset_file_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningresource',
            name='url_name',
            field=models.TextField(null=True),
        ),
    ]
