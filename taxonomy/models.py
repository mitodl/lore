"""Models for lore taxonomy application"""

from django.db import models


class Vocabulary(models.Model):
    """Model for vocabulary table"""
    repository = models.ForeignKey("Repository")
    name = models.TextField()
    description = models.TextField()
    required = models.BooleanField()
    vocabulary_type = models.CharField(max_length=1, choices=(
        ("m", "managed"),
        ("f", "free tagging")
    ))
    weight = models.IntegerField()

    learning_object_types = models.ManyToManyField("LearningObjectType")


class Term(models.Model):
    """Model for term table"""
    vocabulary = models.ForeignKey("Vocabulary")
    label = models.TextField()
    weight = models.IntegerField()

    learning_objects = models.ManyToManyField("LearningObject")
