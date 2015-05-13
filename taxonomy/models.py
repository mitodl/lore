"""Models for lore taxonomy application"""

from django.db import models


class Vocabulary(models.Model):
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
    vocabulary = models.ForeignKey("Vocabulary")
    learning_object_type = models.ForeignKey("LearningObjectType")


class Term(models.Model):
    vocabulary = models.ForeignKey("Vocabulary")
    label = models.TextField()
    weight = models.IntegerField()


class LearningObjectTerm(models.Model):
    learning_object = models.ForeignKey("LearningObject")
    term = models.ForeignKey("Term")
