"""APIs for lore taxonomy application"""

from taxonomy.models import Vocabulary, Term
from learningobjects.models import LearningObject, LearningObjectType


def get_vocabulary(vocabulary_id):
    """
    Lookup vocabulary given its id
    :param vocabulary_id: Vocabulary id
    :return: Dictionary for vocabulary
    """
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)

    return _get_vocabulary_from_model(vocabulary)


def _get_vocabulary_from_model(vocabulary):
    """
    Convert vocabulary model to dictionary
    :param vocabulary: Vocabulary model
    :return: Dictionary
    """
    learning_object_types = [
        t.name for t in vocabulary.learning_object_types.all()]

    # TODO: double check how Django exposes vocabulary_type
    return {
        "repository_id": vocabulary.repository_id,
        "name": vocabulary.name,
        "description": vocabulary.description,
        "required": vocabulary.required,
        "vocabulary_type": vocabulary.vocabulary_type,
        "weight": vocabulary.weight,
        "learning_object_types": learning_object_types,
    }


def create_vocabulary(
        repository_id, name, description, required, vocabulary_type, weight,
        learning_object_types):
    """
    Create a vocabulary and save it in database
    :param repository_id: An existing repository id
    :param name: Name of vocabulary
    :param description: Description of vocabulary
    :param required: Is vocabulary required?
    :param vocabulary_type: Type of vocabulary (either "managed" or
     "free tagging")
    :param weight: Weight, as integer
    :param learning_object_types: List of valid learning object types
    :return:
    """

    learning_object_types_models = LearningObjectType.objects.filter(
        name__in=learning_object_types)

    vocabulary = Vocabulary.objects.create(
        repository_id=repository_id,
        name=name,
        description=description,
        required=required,
        vocabulary_type=vocabulary_type,
        weight=weight,
        learning_object_types=learning_object_types_models,
    )

    return _get_vocabulary_from_model(vocabulary)


def update_vocabulary(vocabulary_id,
                      repository_id, name, description, required,
                      vocabulary_type, weight,
                      learning_object_types):
    """
    Update an existing vocabulary
    :param vocabulary_id: An existing vocabulary id
    :param repository_id: An existing repository id
    :param name: Name of vocabulary
    :param description: Description of vocabulary
    :param required: Is vocabulary required?
    :param vocabulary_type: Type of vocabulary (either "managed" or
    "free tagging")
    :param weight: int
    :param learning_object_types: List of valid learning object types
    :return:
    """
    learning_object_types_models = LearningObjectType.objects.filter(
        name__in=learning_object_types)

    Vocabulary.objects.update(
        id=vocabulary_id,
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
    Delete vocabulary with given id
    :param vocabulary_id:
    :return:
    """
    Vocabulary.objects.filter(id=vocabulary_id).delete()


def get_term(term_id):
    """
    Get term given term id
    :param term_id: Term id
    :return: Term
    """
    return _get_term_from_model(Term.objects.get(id=term_id))


def _get_term_from_model(term):
    """
    Convert Term model to dictionary
    :param term: Term
    :type term: Term
    :return: Dictionary
    """
    return {
        "vocabulary_id": term.vocabulary_id,
        "label": term.label,
        "weight": term.weight,
        "learning_object_ids": [x.id for x in term.learning_objects]
    }


def create_term(vocabulary_id, label, weight, learning_object_ids):
    """
    Create new Term and save it in database
    :param vocabulary_id: Existing vocabulary id
    :param label: Label
    :param weight: Integer weight
    :param learning_object_ids: List of existing learning object ids
    :return: The new term
    """
    # TODO: can learning_object_ids be passed in like this?
    term = Term.objects.create(
        vocabulary_id=vocabulary_id,
        label=label,
        weight=weight,
        learning_object_ids=learning_object_ids)

    return _get_term_from_model(term)


def update_term(term_id, vocabulary_id, label, weight, learning_object_ids):
    # TODO: what if user just wants to update a single field?
    Term.objects.update(
        term_id=term_id,
        vocabulary_id=vocabulary_id,
        label=label,
        weight=weight,
        learning_object_ids=learning_object_ids
    )


def delete_term(term_id):
    """
    Delete term with id term_id
    :param term_id: Term id
    :return: None
    """
    Term.objects.filter(id=term_id).delete()


def get_learning_objects_for_term(term_id):
    learning_objects = Term.objects.get(id=term_id).learning_objects
    return [_get_learning_object_from_model(learning_object)
            for learning_object in learning_objects]


def get_term_for_learning_object(learning_object_id):
    terms = LearningObject.objects.get(id=learning_object_id).terms
    return [_get_term_from_model(term) for term in terms]


def add_term_to_learning_object(learning_object_id, term_id):
    # TODO: a way to do this without the unnecessary get()s?
    learning_object = LearningObject.objects.get(id=learning_object_id)
    term = Term.objects.get(id=term_id)
    learning_object.terms.add(term)


def remove_term_from_learning_object(learning_object_id, term_id):
    # TODO: a way to do this without the unnecessary get()?
    term = Term.objects.get(id=term_id)
    term.learning_objects.filter(id=learning_object_id).delete()


def get_vocabularies_for_learning_object_type(learning_object_type_name):
    vocabularies = Vocabulary.objects.filter(
        learning_object_types__name=learning_object_type_name)
    return [_get_vocabulary_from_model(vocabulary)
            for vocabulary in vocabularies]


def get_learning_object_types_for_vocabulary(vocabulary_id):
    learning_object_types = LearningObjectType.objects.filter(
        vocabulary__id=vocabulary_id
    )
    return [x.name for x in learning_object_types]


def add_learning_object_type_for_vocabulary(learning_object_type,
                                            vocabulary_id):
    # TODO: extra get probably unnecessary
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    learning_object_type = LearningObjectType.objects.get(
        name=learning_object_type)
    vocabulary.learning_object_types.add(learning_object_type)


def remove_learning_object_type_from_vocabulary(learning_object_type,
                                                vocabulary_id):
    # TODO: extra get probably unnecessary
    vocabulary = Vocabulary.objects.get(id=vocabulary_id)
    vocabulary.learning_object_types.filter(name=learning_object_type).delete()