# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations
from django.utils.timezone import utc

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0004_static_assets'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 19, 114680, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 20, 410676, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='learningresource',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 21, 522626, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='learningresource',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 22, 770622, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 24, 114723, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 25, 402653, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='repository',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 26, 858744, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='repository',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 18, 19, 28, 170661, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staticasset',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 21, 11, 38, 480507, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staticasset',
            name='date_modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 21, 11, 42, 9869, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
