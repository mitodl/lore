# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import learningresources.models
# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0003_add_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asset', models.FileField(upload_to=learningresources.models.static_asset_basepath)),
                ('course', models.ForeignKey(to='learningresources.Course')),
                ('learning_resources', models.ManyToManyField(to='learningresources.LearningResource', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='learningresource',
            name='static_assets',
            field=models.ManyToManyField(to='learningresources.StaticAsset', blank=True),
        ),
    ]
