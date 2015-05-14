"""Models for lore taxonomy application"""

from django.db import models

from learningobjects.models import (
    Repository,
    LearningObjectType,
    LearningObject,
)


class Vocabulary(models.Model):
    """Model for vocabulary table"""
    repository = models.ForeignKey(Repository)
    name = models.TextField()
    description = models.TextField()
    required = models.BooleanField()
    vocabulary_type = models.CharField(max_length=1, choices=(
        ("m", "managed"),
        ("f", "free tagging")
    ))
    weight = models.IntegerField()

    learning_object_types = models.ManyToManyField(LearningObjectType,
                                                   related_name="vocabularies")


class Term(models.Model):
    """Model for term table"""
    vocabulary = models.ForeignKey(Vocabulary)
    label = models.TextField()
    weight = models.IntegerField()

    learning_objects = models.ManyToManyField(LearningObject,
                                              related_name="terms")


def get_vocabulary(vocabulary_id):
    return Vocabulary.objects.get(id=vocabulary_id)


def create_vocabulary(**kwargs):
    return Vocabulary.objects.create(**kwargs)


def update_vocabulary(**kwargs):
    return Vocabulary.objects.update(**kwargs)


def delete_vocabulary(vocabulary_id):
    Vocabulary.objects.filter(id=vocabulary_id).delete()


def get_term(term_id):
    return Term.objects.get(id=term_id)


def create_term(**kwargs):
    return Term.objects.create(**kwargs)


def update_term(**kwargs):
    return Term.objects.update(**kwargs)


def delete_term(term_id):
    Term.objects.filter(id=term_id).delete()


def get_learning_objects_for_term(term_id):
    return Term.objects.get(id=term_id).learning_objects


def get_term_for_learning_object(learning_object_id):
    return LearningObject.objects.get(id=learning_object_id).terms


def add_term_to_learning_object(learning_object_id, term_id):
    # TODO: a way to do this without the unnecessary get()s?
    learning_object = LearningObject.objects.get(id=learning_object_id)
    term = Term.objects.get(id=term_id)
    learning_object.terms.add(term)


def remove_term_from_learning_object(learning_object_id, term_id):
    # TODO: a way to do this without the unnecessary get()s?
    term = Term.objects.get(id=term_id)
    term.learning_objects.filter(id=learning_object_id).delete()


def get_vocabularies_for_learning_object_type(learning_object_type_name):
    return Vocabulary.objects.filter(
        learning_object_types__name=learning_object_type_name)


def get_learning_object_types_for_vocabulary(vocabulary_id):
    return LearningObjectType.objects.filter(
        vocabulary__id=vocabulary_id
    )


def add_learning_object_type_for_vocabulary(learning_object_type, vocabulary_id):
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    learning_object_type = LearningObjectType.objects.get(name=learning_object_type)
    vocabulary.learning_object_types.add(learning_object_type)


def remove_learning_object_type_from_vocabulary(learning_object_type, vocabulary_id):
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    vocabulary.learning_object_types.filter(name=learning_object_type).delete()