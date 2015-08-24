"""
Signals for the Taxonomy application.

This file was created because we need to create the curator vocabulary
when a new Repository is created, but we can't add it to
Repository.save() because that would create a circular import.

The custom "repo_created" signal was added because if we use
post_sav" here, there is a race condition with the post_save
in roles which adds admin permissions to a Repository to the user
who created it. It is impossible to dictate the order in which
signals will be executed, and there's even a "wontfix" ticket for it:
https://code.djangoproject.com/ticket/16547
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from learningresources.models import (
    repo_created, Repository, LearningResource,
)

log = logging.getLogger(__name__)

CURATION_VOCAB_NAME = "curation status"


# pylint: disable=unused-argument
@receiver(repo_created)
def create_default_vocabulary(sender, **kwargs):
    """
    Create the default curator vocabulary when a repository
    is created.
    """
    if not isinstance(sender, Repository):
        return
    from taxonomy.utils import create_curator_vocabulary
    from learningresources.models import LearningResourceType
    vocabulary = create_curator_vocabulary(
        repo_slug=sender.slug,
        user_id=sender.created_by.id,
        name=CURATION_VOCAB_NAME,
        description=CURATION_VOCAB_NAME,
    )
    for resource_type in LearningResourceType.objects.all():
        vocabulary.learning_resource_types.add(resource_type)


@receiver(post_save)
def add_default_curation_term(sender, **kwargs):
    """
    Add the default curation term to each newly-created LearningResource.
    """
    if kwargs["created"] is False:
        return
    instance = kwargs["instance"]
    if not isinstance(instance, LearningResource):
        return
    from taxonomy.models import Term
    terms = Term.objects.filter(
        vocabulary__repository__id=instance.course.repository_id,
        vocabulary__name=CURATION_VOCAB_NAME,
        label=Term.EMPTY_VALUE,
    )
    if terms.count() != 1:
        log.error(
            (
                "Unable to add default curation status value to "
                "learning resource pk %s. Expected 1 matching "
                "term, found %s."
            ), instance.id, terms.count()
        )
        return
    instance.terms.add(terms[0])
