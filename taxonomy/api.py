"""APIs for lore taxonomy application"""
from __future__ import unicode_literals

from taxonomy.models import (
    Vocabulary,
    Term,
)
from learningresources.api import (
    get_repo,
    NotFound,
)


def get_vocabulary(repo_slug, user_id, vocab_slug):
    """
    Lookup vocabulary given its slug, using repo_slug to validate ownership.

    Args:
        repo_id (int): Repository id
        user_id (int): User id
        vocab_slug (unicode): Vocabulary slug

    Returns:
        Vocabulary (Vocabulary): The vocabulary from the database
    """
    repo = get_repo(repo_slug, user_id)
    try:
        return repo.vocabulary_set.get(slug=vocab_slug)
    except Vocabulary.DoesNotExist:
        raise NotFound()


def get_term(repo_slug, user_id, vocab_slug, term_slug):
    """
    Get Term with existing slug, validating ownership for repo_slug
    and vocab_slug.

    Args:
        term_id (int): Term slug

    Returns:
        Term (Term): The Term with the id
    """
    repo = get_repo(repo_slug, user_id)
    try:
        return repo.vocabulary_set.get(
            slug=vocab_slug
        ).term_set.get(
            slug=term_slug
        )
    except Vocabulary.DoesNotExist:
        raise NotFound()
    except Term.DoesNotExist:
        raise NotFound()


# pylint: disable=too-many-arguments
def create_vocabulary(
        user_id, repo_slug, name, description,
        required=False, vocabulary_type=Vocabulary.MANAGED, weight=0,
        multi_terms=False):
    """
    Create a new vocabulary.
    Args:
        user_id (int): primary key of the User
        repo_slug (unicode): slug of the repository
        name (unicode): vocab name
        description (unicode): vocab description
        required (bool): is it required?
        vocabulary_type (unicode): on of the Vocabulary.vocabulary_type options
        weight (int): vocab weight
        multi_terms (bool): multiple terms possible on one LearningResource
    Returns:
        vocab (Vocabulary)
    """
    repo = get_repo(repo_slug, user_id)
    vocab = Vocabulary.objects.create(
        repository_id=repo.id,
        name=name, description=description,
        required=required, vocabulary_type=vocabulary_type,
        weight=weight, multi_terms=multi_terms
    )
    return vocab
