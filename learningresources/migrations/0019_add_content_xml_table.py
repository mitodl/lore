# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0018_fill_empty_slugs'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningResourceContentXml',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('content_xml', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='learningresource',
            name='content_xml',
            field=models.TextField(null=True)
        ),
        migrations.AddField(
            model_name='learningresource',
            name='content_xml_model',
            field=models.ForeignKey(null=True, default=None, to='learningresources.LearningResourceContentXml'),
            preserve_default=False,
        ),
    ]
