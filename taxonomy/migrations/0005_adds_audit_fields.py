# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations
from django.utils.timezone import utc

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0004_finish_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 29, 506705, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='term',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 31, 650700, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 33, 42693, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 34, 210680, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
