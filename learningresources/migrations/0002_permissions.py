# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='repository',
            options={'permissions': (
                        ('view_repo', 'Permission to view the repository'),
                        ('import_course',
                         'Permission to import course in repository'),
                        ('manage_taxonomy',
                         'Permission to manage repository taxonomy'),
                        ('add_edit_metadata',
                         'Permission to add or edit metadata')
                    )},
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set([('repository', 'org',
                                  'course_number', 'run')]),
        ),
    ]
