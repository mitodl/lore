# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0006_auto_20150630_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='multi_terms',
            field=models.BooleanField(default=False),
        ),
    ]
