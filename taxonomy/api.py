"""APIs for lore taxonomy application"""

from taxonomy.models import Vocabulary, Term
from learningobjects.models import LearningObject, LearningObjectType


def get_vocabulary(vocabulary_id):
    """
    Lookup vocabulary given its id

    Args:
        vocabulary_id (int): Vocabulary id

    Returns:
        Vocabulary: The vocabulary from the database
    """
    return Vocabulary.objects.get(id=vocabulary_id)


def create_vocabulary(
        repository_id, name, description, required, vocabulary_type, weight,
        learning_object_types):
    """
    Create a Vocabulary and save it in database

    Args:
        repository_id (int): Repository id
        name (unicode): Name of Vocabulary
        description (unicode): Description of Vocabulary
        required (bool): Is Vocabulary required?
        vocabulary_type (unicode): Vocabulary type
        weight (int): Weight
        learning_object_types (list of unicode): Valid learning object types

    Returns:
        Vocabulary: The Vocabulary which was just added to the database

    """

    learning_object_types_models = LearningObjectType.objects.filter(
        name__in=learning_object_types
    )

    return Vocabulary.objects.create(
        repository_id=repository_id,
        name=name,
        description=description,
        required=required,
        vocabulary_type=vocabulary_type,
        weight=weight,
        learning_object_types=learning_object_types_models,
    )


def delete_vocabulary(vocabulary_id):
    """
    Delete Vocabulary with given id

    Args:
        vocabulary_id (int): Vocabulary id
    """
    Vocabulary.objects.filter(id=vocabulary_id).delete()


def get_term(term_id):
    """
    Get Term with existing id

    Args:
        term_id (int): Term id

    Returns:
        Term: The Term with the id
    """
    return Term.objects.get(id=term_id)


def create_term(vocabulary_id, label, weight, learning_object_ids):
    """
    Create new Term and save it in database

    Args:
        vocabulary_id (int): Vocabulary id
        label (unicode): Term label
        weight (int): Weight for term
        learning_object_ids (list of int): Id numbers for
            existing learning objects

    Returns:
        Term: The newly created Term

    """
    return Term.objects.create(
        vocabulary_id=vocabulary_id,
        label=label,
        weight=weight,
        learning_object_ids=learning_object_ids)


def delete_term(term_id):
    """
    Delete an existing Term

    Args:
        term_id (int): Term id
    """
    Term.objects.filter(id=term_id).delete()


def get_learning_objects_for_term(term_id):
    """
    Get LearningObjects using a particular Term

    Args:
        term_id (int): Term id

    Returns:
        sequence of LearningObject relating to existing Term
    """
    return Term.objects.get(id=term_id).learning_objects


def get_terms_for_learning_object(learning_object_id):
    """
    Get Terms using a particular LearningObject

    Args:
        learning_object_id (int): Learning object id

    Returns:
        sequence of Term relating to existing LearningObject
    """
    return LearningObject.objects.get(id=learning_object_id).terms


def add_term_to_learning_object(learning_object_id, term_id):
    """
    Add existing Term with id term_id to a particular LearningObject
    with id learning_object_id

    Args:
        learning_object_id (int): Id for LearningObject
        term_id (int): Id for Term
    """
    learning_object = LearningObject.objects.get(id=learning_object_id)
    term = Term.objects.get(id=term_id)
    learning_object.terms.add(term)


def remove_term_from_learning_object(learning_object_id, term_id):
    """
    Remove existing Term with id term_id from a LearningObject with id
    learning_object_id

    Args:
        learning_object_id (int): Id for LearningObject
        term_id (int): Id for Term
    """
    term = Term.objects.get(id=term_id)
    term.learning_objects.filter(id=learning_object_id).delete()


def get_vocabularies_for_type(learning_object_type):
    """
    Get vocabularies supporting the given learning object type

    Args:
        learning_object_type (unicode): The learning object type

    Returns:
        sequence of Vocabulary objects supporting the learning object type
    """
    return Vocabulary.objects.filter(
        learning_object_types__name=learning_object_type
    )


def get_types_for_vocabulary(vocabulary_id):
    """
    Get learning object types supported by a Vocabulary

    Args:
        vocabulary_id (int): Id for existing Vocabulary

    Returns:
        list of unicode: sequence of learning object types supported by
            a LearningObject
    """
    learning_object_types = LearningObjectType.objects.filter(
        vocabulary__id=vocabulary_id
    )
    return [x.name for x in learning_object_types]


def add_type_for_vocabulary(learning_object_type,
                            vocabulary_id):
    """
    Add learning object type to an existing Vocabulary

    Args:
        learning_object_type (unicode): A learning object type
        vocabulary_id (int): Id for existing Vocabulary
    """
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    learning_object_type = LearningObjectType.objects.get(
        name=learning_object_type)
    vocabulary.learning_object_types.add(learning_object_type)


def remove_type_from_vocabulary(learning_object_type,
                                vocabulary_id):
    """
    Remove learning object type from existing Vocabulary

    Args:
        learning_object_type (unicode): A learning object type
        vocabulary_id (int): Id for existing Vocabulary
    """
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    vocabulary.learning_object_types.filter(name=learning_object_type).delete()
