"""Models for lore taxonomy application"""
from __future__ import unicode_literals

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from audit.models import BaseModel
from learningresources.models import (
    Repository,
    LearningResourceType,
    LearningResource,
)
from rest.util import default_slugify


def make_vocab_key(vocab_id):
    """
    Create vocab key used for elasticsearch index mapping.
    """
    return "vocab_{id}".format(id=vocab_id)


class Vocabulary(BaseModel):
    """Model for vocabulary table"""
    MANAGED = "m"
    FREE_TAGGING = "f"

    repository = models.ForeignKey(Repository)
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
    multi_terms = models.BooleanField(default=False)

    class Meta:
        # pylint: disable=missing-docstring
        unique_together = (("repository", "name"),)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle slugs."""
        if self.id is None or self.name != get_object_or_404(
                Vocabulary, id=self.id).name:
            self.slug = default_slugify(
                self.name,
                Vocabulary._meta.model_name,
                lambda slug: Vocabulary.objects.filter(slug=slug).exists()
            )

        return super(Vocabulary, self).save(*args, **kwargs)

    @property
    def index_key(self):
        """Key used in elasticsearch index."""
        return make_vocab_key(self.id)


class Term(BaseModel):
    """Model for term table"""
    vocabulary = models.ForeignKey(Vocabulary)
    label = models.CharField(max_length=256)
    slug = models.CharField(max_length=256, unique=True)
    weight = models.IntegerField()

    learning_resources = models.ManyToManyField(
        LearningResource,
        related_name="terms",
    )

    class Meta:
        # pylint: disable=missing-docstring
        unique_together = (('vocabulary', 'label'),)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle slugs."""
        if self.id is None or self.label != get_object_or_404(
                Term, id=self.id).label:
            self.slug = default_slugify(
                self.label,
                Term._meta.model_name,
                lambda slug: Term.objects.filter(slug=slug).exists()
            )
        return super(Term, self).save(*args, **kwargs)
