# -*- coding: utf-8 -*-

"""
This migration should be able to be copy-pasted exactly for any
future changes to the mapping, with the exception of the dependencies, which
should be updated.
"""

from __future__ import unicode_literals

from django.db import migrations

# pylint: skip-file


def create_learning_resource_mapping(apps, schema_editor):
    pass  # changed to no-op


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0016_revert_backfill'),
        ('taxonomy', '0007_vocabulary_multi_terms'),
    ]

    operations = [
        migrations.RunPython(create_learning_resource_mapping)
    ]
