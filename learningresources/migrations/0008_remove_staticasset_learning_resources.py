# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0007_remove_old_date_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staticasset',
            name='learning_resources',
        ),
    ]
