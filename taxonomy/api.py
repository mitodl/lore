"""APIs for lore taxonomy application"""
from __future__ import unicode_literals

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningresources.models import (
    LearningResource,
    LearningResourceType,
)


def get_vocabulary(vocabulary_id):
    """
    Lookup vocabulary given its id.

    Args:
        vocabulary_id (int): Vocabulary id

    Returns:
        Vocabulary (Vocabulary): The vocabulary from the database
    """
    return get_object_or_404(Vocabulary, id=vocabulary_id)


# pylint: disable=too-many-arguments
@transaction.atomic
def create_vocabulary(
        repository_id, name, description, required, vocabulary_type, weight
):
    """
    Create a Vocabulary and save it in database.

    Args:
        repository_id (int): Repository id
        name (unicode): Name of Vocabulary
        description (unicode): Description of Vocabulary
        required (bool): Is Vocabulary required?
        vocabulary_type (unicode): Vocabulary type
        weight (int): Weight

    Returns:
        Vocabulary (Vocabulary): The Vocabulary which was just
        added to the database

    """

    vocabulary = Vocabulary(
        repository_id=repository_id,
        name=name,
        description=description,
        required=required,
        vocabulary_type=vocabulary_type,
        weight=weight,
    )
    slug = slugify(vocabulary.name)
    count = 1
    while Vocabulary.objects.filter(slug=slug).exists():
        slug = "{0}{1}".format(slugify(vocabulary.name), count)
        count += 1
    vocabulary.slug = slug
    vocabulary.full_clean()
    vocabulary.save()
    return vocabulary


def delete_vocabulary(vocabulary_id):
    """
    Delete Vocabulary with given id.

    Args:
        vocabulary_id (int): Vocabulary id
    """
    get_object_or_404(Vocabulary, id=vocabulary_id).delete()


def get_term(term_id):
    """
    Get Term with existing id.

    Args:
        term_id (int): Term id

    Returns:
        Term (Term): The Term with the id
    """
    return get_object_or_404(Term, id=term_id)


@transaction.atomic
def create_term(vocabulary_id, label, weight):
    """
    Create new Term and save it in database.

    Args:
        vocabulary_id (int): Vocabulary id
        label (unicode): Term label
        weight (int): Weight for term

    Returns:
        Term (Term): The newly created Term
    """
    term = Term(
        vocabulary_id=vocabulary_id,
        label=label,
        weight=weight
    )
    term.full_clean()
    term.save()
    return term


def delete_term(term_id):
    """
    Delete Term with given id.

    Args:
        term_id (int): Term id
    """
    get_object_or_404(Term, id=term_id).delete()


def get_learning_resources_for_term(term_id):
    """
    Get LearningResources for a particular Term.

    Learning resources are ordered by ``id``.

    Args:
        term_id (int): Term id

    Returns:
        sequence of LearningResource relating to existing Term
    """
    return get_object_or_404(
        Term,
        id=term_id
    ).learning_resources.order_by('id')


def get_terms_for_learning_resource(learning_resource_id):
    """
    Get Terms using a particular LearningResource.

    Args:
        learning_resource_id (int): Learning object id

    Returns:
        sequence of Term relating to existing LearningResource
    """
    return get_object_or_404(
        LearningResource, id=learning_resource_id).terms.order_by('label')


@transaction.atomic
def add_term_to_learning_resource(learning_resource_id, term_id):
    """
    Add existing Term to a particular LearningResource.

    Add existing Term with id ``term_id`` to a particular LearningResource
    with id ``learning_resource_id``.

    Args:
        learning_resource_id (int): Id for LearningResource
        term_id (int): Id for Term
    """
    learning_resource = get_object_or_404(LearningResource,
                                          id=learning_resource_id)
    term = get_object_or_404(Term, id=term_id)
    learning_resource.terms.add(term)


# pylint complains that name has 33 characters when the max is 30
# pylint: disable=invalid-name
@transaction.atomic
def remove_term_from_learning_resource(learning_resource_id, term_id):
    """
    Remove Term from LearningResource.

    Remove existing Term with id ``term_id`` from a LearningResource with id
    ``learning_resource_id``.

    Args:
        learning_resource_id (int): Id for LearningResource
        term_id (int): Id for Term
    """
    term = get_object_or_404(Term, id=term_id)
    learning_resource = get_object_or_404(LearningResource,
                                          id=learning_resource_id)
    term.learning_resources.remove(learning_resource)


def get_vocabularies_for_type(learning_resource_type):
    """
    Get vocabularies supporting the given learning object type.

    Vocabularies are ordered by ``name``.

    Args:
        learning_resource_type (unicode): The learning resource type

    Returns:
        sequence of Vocabulary objects supporting the learning resource type
    """
    return get_object_or_404(
        LearningResourceType,
        name=learning_resource_type
    ).vocabularies.order_by('name')


def get_types_for_vocabulary(vocabulary_id):
    """
    Get learning object types supported by a Vocabulary.

    Args:
        vocabulary_id (int): Id for existing Vocabulary

    Returns:
        list (list of unicode): sequence of learning object types supported by
        a LearningResource
    """
    learning_resource_types = get_object_or_404(
        Vocabulary, id=vocabulary_id
    ).learning_resource_types.order_by('name')

    return [x.name for x in learning_resource_types]


@transaction.atomic
def add_type_for_vocabulary(learning_resource_type,
                            vocabulary_id):
    """
    Add learning object type to an existing Vocabulary.

    Args:
        learning_resource_type (unicode): A learning object type
        vocabulary_id (int): Id for existing Vocabulary
    """
    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    learning_resource_type = get_object_or_404(LearningResourceType,
                                               name=learning_resource_type)
    vocabulary.learning_resource_types.add(learning_resource_type)


@transaction.atomic
def remove_type_from_vocabulary(learning_resource_type_name,
                                vocabulary_id):
    """
    Remove learning object type from existing Vocabulary.

    Args:
        learning_resource_type (unicode): A learning object type
        vocabulary_id (int): Id for existing Vocabulary
    """
    vocabulary = get_object_or_404(Vocabulary, id=vocabulary_id)
    learning_resource_type = get_object_or_404(
        LearningResourceType,
        name=learning_resource_type_name
    )
    vocabulary.learning_resource_types.remove(learning_resource_type)
