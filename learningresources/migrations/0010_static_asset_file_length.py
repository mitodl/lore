# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import learningresources.models

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0009_allow_blank_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticasset',
            name='asset',
            field=models.FileField(
                max_length=900,
                upload_to=learningresources.models.static_asset_basepath
            ),
        ),
    ]
