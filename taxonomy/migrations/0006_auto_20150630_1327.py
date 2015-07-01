# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0005_adds_audit_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='vocabulary',
            field=models.ForeignKey(to='taxonomy.Vocabulary'),
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='repository',
            field=models.ForeignKey(to='learningresources.Repository'),
        ),
    ]
