# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F

# pylint: skip-file


def transfer_datetimes(apps, schema_editor):
    """Move the added/edited stamps to the new, universal fields."""
    Course = apps.get_model("learningresources", "Course")
    Course.objects.all().update(date_created=F("import_date"))

    Repository = apps.get_model("learningresources", "Repository")
    Repository.objects.all().update(date_created=F("create_date"))


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0005_auto_adds_audit_fields'),
    ]

    operations = [
        migrations.RunPython(transfer_datetimes)
    ]
