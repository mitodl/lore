"""
Revert backfill migration
"""

from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify

# pylint: skip-file

VOCAB_NAME = "curation status"


def revert_backfill(apps, schema_editor):
    """Reverts curation vocabulary and terms and the --not set-- term."""
    Vocabulary = apps.get_model("taxonomy", "Vocabulary")
    Term = apps.get_model("taxonomy", "Term")

    # Delete links between terms and learning resources where term is owned
    # by curation vocabulary
    Term.learning_resources.through.objects.filter(
        term__vocabulary__name=VOCAB_NAME
    ).delete()

    # Delete all curation vocabularies. This will cascade to include terms.
    Vocabulary.objects.filter(name=VOCAB_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0015_backfill_curator_vocabularies'),
    ]

    operations = [
        migrations.RunPython(revert_backfill)
    ]
