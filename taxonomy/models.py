"""Models for lore taxonomy application"""
from __future__ import unicode_literals

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import get_object_or_404

from learningresources.models import (
    Repository,
    LearningResourceType,
    LearningResource,
)


class Vocabulary(models.Model):
    """Model for vocabulary table"""
    MANAGED = "m"
    FREE_TAGGING = "f"

    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    slug = models.CharField(max_length=256, unique=True)
    description = models.TextField(
        help_text=_("Describe how content authors should use this vocabulary")
    )
    required = models.BooleanField()
    vocabulary_type = models.CharField(
        max_length=1,
        choices=(
            (MANAGED, _("Managed")),
            (FREE_TAGGING, _("Tag Style (on the fly)"))
        ),
        default="m",
        help_text=_("Should terms be created in advance or on the fly?")
    )
    weight = models.IntegerField()

    learning_resource_types = models.ManyToManyField(
        LearningResourceType,
        related_name="vocabularies",
        help_text=_("Resource types this vocabulary applies to")
    )

    class Meta:
        # pylint: disable=missing-docstring
        unique_together = (("repository", "name"),)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle slugs."""
        if self.id is None or self.name != get_object_or_404(
                Vocabulary, id=self.id).name:
            slug = slugify(self.name)
            count = 1
            while Vocabulary.objects.filter(slug=slug).exists():
                slug = "{0}{1}".format(slugify(self.name), count)
                count += 1
            self.slug = slug
        return super(Vocabulary, self).save(*args, **kwargs)


class Term(models.Model):
    """Model for term table"""
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.PROTECT)
    label = models.TextField()
    weight = models.IntegerField()

    learning_resources = models.ManyToManyField(LearningResource,
                                                related_name="terms")

    class Meta:
        # pylint: disable=missing-docstring
        unique_together = (('vocabulary', 'label'),)
