# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


# pylint: skip-file
def generate_term_slugs(apps, schema_editor):
    """
    Generate slugs for terms
    """
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Term = apps.get_model("taxonomy", "Term")
    for term in Term.objects.all():
        slug = slugify(term.label)  # pragma: no cover

        count = 1  # pragma: no cover
        while Term.objects.filter(slug=slug).exists():  # pragma: no cover
            slug = "{0}{1}".format(slugify(term.label), count)  # pragma: no cover
            count += 1  # pragma: no cover
        term.slug = slug  # pragma: no cover
        term.save()  # pragma: no cover


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0002_add_slug_field'),
    ]

    operations = [
        migrations.RunPython(generate_term_slugs),
    ]
