# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0020_move_content_xml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningresource',
            name='content_xml_model',
            field=models.ForeignKey(to='learningresources.LearningResourceContentXml'),
            preserve_default=False,
        ),
    ]

