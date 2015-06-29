# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0006_move_datestamp_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='import_date',
        ),
        migrations.RemoveField(
            model_name='repository',
            name='create_date',
        ),
    ]
