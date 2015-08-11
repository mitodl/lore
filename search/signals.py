"""
Initialize signals for indexing the search engine. This allows us to
automatically update the index for a LearningResource when it has terms
added to or removed from a vocabulary. The HAYSTACK_SIGNAL_PROCESSOR value
in settings.py handles the save of a LearningResource, but not
many-to-many fields.
"""

import logging

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from search.search_indexes import LearningResourceIndex, get_vocabs

log = logging.getLogger(__name__)


# pylint: disable=unused-argument
@receiver(m2m_changed)
def handle_m2m_save(sender, **kwargs):
    """Update index when taxonomies are updated."""
    instance = kwargs.pop("instance", None)
    if instance.__class__.__name__ != "LearningResource":
        return
    # Update cache for the LearningResource if it's already set.
    get_vocabs(instance.course_id, instance.id, solo_update=True)
    LearningResourceIndex().update_object(instance)
