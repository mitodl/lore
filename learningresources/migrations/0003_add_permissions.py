# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0002_permissions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='repository',
            options={'permissions': (
                ('view_repo',
                 'Permission to view the repository'),
                ('import_course',
                 'Permission to import course in repository'),
                ('manage_taxonomy',
                 'Permission to manage repository taxonomy'),
                ('add_edit_metadata',
                 'Permission to add or edit metadata'),
                ('manage_repo_users',
                 'Permission manage users for the repository')
            )},
        ),
    ]
