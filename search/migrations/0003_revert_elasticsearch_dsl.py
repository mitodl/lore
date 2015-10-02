# -*- coding: utf-8 -*-

"""
This migration should be able to be copy-pasted exactly for any
future changes to the mapping, with the exception of the dependencies, which
should be updated.
"""

from __future__ import unicode_literals

from django.db import models, migrations

from search.utils import create_mapping, index_resources

# pylint: skip-file


def update_mapping(apps, schema_editor):
    create_mapping()

class Migration(migrations.Migration):

    dependencies = [
        ('search', "0002_update_mapping"),
    ]

    operations = [
        migrations.RunPython(update_mapping)
    ]
