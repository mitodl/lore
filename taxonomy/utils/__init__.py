"""
Utilities for the taxonomy application.
"""

import logging

from django.utils.text import slugify

log = logging.getLogger(__name__)


def create_curator_vocabulary(repo_slug, user_id, name, description):
    """
    Create the default "curator" vocabulary for a repository.
    Args:
        repo_slug (unicode): slug of the repository
        user_id (int): primary key of the User
        name (unicode): vocab name
        description (unicode): vocab description

    Returns:
        vocab (Vocabulary)
    """
    from taxonomy.api import create_vocabulary
    from taxonomy.models import Term
    vocabulary = create_vocabulary(
        user_id=user_id,
        repo_slug=repo_slug,
        name=name,
        description=description,
    )
    labels = (
        'ready to use', 'tagged', 'course information',
        'discarded', 'hidden',
    )
    for label in labels:
        Term.objects.create(
            vocabulary_id=vocabulary.id,
            label=label,
            slug=slugify("{0}_{1}_auto".format(label, vocabulary.id)),
            weight=0,
        )
    return vocabulary
