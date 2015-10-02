# -*- coding: utf-8 -*-

"""
This migration should be able to be copy-pasted exactly for any
future changes to the mapping, with the exception of the dependencies, which
should be updated.
"""

from __future__ import unicode_literals

from django.db import migrations

# pylint: skip-file


def update_mapping(apps, schema_editor):
    pass  # Changed to no-op


class Migration(migrations.Migration):

    dependencies = [
        ('search', "0001_initial"),
        ('learningresources', '0017_learningresource_missing_title_update'),
        ('taxonomy', '0007_vocabulary_multi_terms'),
    ]

    operations = [
        migrations.RunPython(update_mapping)
    ]
