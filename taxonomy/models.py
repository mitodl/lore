"""Models for lore taxonomy application"""
from __future__ import unicode_literals

from django.db import models

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
    name = models.TextField()
    description = models.TextField()
    required = models.BooleanField()
    vocabulary_type = models.CharField(max_length=1, choices=(
        (MANAGED, "managed"),
        (FREE_TAGGING, "free tagging")
    ))
    weight = models.IntegerField()

    learning_resource_types = models.ManyToManyField(
        LearningResourceType,
        related_name="vocabularies"
    )

    # pylint: disable=missing-docstring,no-init,too-few-public-methods,
    # pylint: disable=old-style-class
    class Meta:
        unique_together = (("repository", "name"),)


class Term(models.Model):
    """Model for term table"""
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.PROTECT)
    label = models.TextField()
    weight = models.IntegerField()

    learning_resources = models.ManyToManyField(LearningResource,
                                                related_name="terms")

    # pylint: disable=missing-docstring,no-init,too-few-public-methods,
    # pylint: disable=old-style-class
    class Meta:
        unique_together = (('vocabulary', 'label'),)
