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


class VocabularyObjectType(models.Model):
    """Model for vocabulary_object_type table"""
    vocabulary = models.ForeignKey("Vocabulary")
    learning_object_type = models.ForeignKey("LearningObjectType")


class Term(models.Model):
    """Model for term table"""
    vocabulary = models.ForeignKey("Vocabulary")
    label = models.TextField()
    weight = models.IntegerField()


class LearningObjectTerm(models.Model):
    """Model for learning_object_term table"""
    learning_object = models.ForeignKey("LearningObject")
    term = models.ForeignKey("Term")
