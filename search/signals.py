"""
Initialize signals for indexing the search engine. This allows us to
automatically update the index for a LearningResource when it has terms
added to or removed from a vocabulary. The HAYSTACK_SIGNAL_PROCESSOR value
in settings.py handles the save of a LearningResource, but not
many-to-many fields.
"""

import logging

from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from haystack.signals import RealtimeSignalProcessor
from statsd.defaults.django import statsd

log = logging.getLogger(__name__)


class LoreRealTimeSignalProcessor(RealtimeSignalProcessor):
    """
    Add timers for Haystack signal processing.
    """
    @statsd.timer('lore.haystack.save_signal')
    def handle_save(self, sender, instance, **kwargs):
        super(LoreRealTimeSignalProcessor, self).handle_save(
            sender, instance, **kwargs
        )

    @statsd.timer('lore.haystack.delete_signal')
    def handle_delete(self, sender, instance, **kwargs):
        super(LoreRealTimeSignalProcessor, self).handle_delete(
            sender, instance, **kwargs
        )


# pylint: disable=unused-argument
@statsd.timer('lore.haystack.taxonomy_update')
@receiver(m2m_changed)
def handle_m2m_save(sender, **kwargs):
    """Update index when taxonomies are updated."""
    from search.search_indexes import LearningResourceIndex, get_vocabs
    instance = kwargs.pop("instance")
    if instance.__class__.__name__ != "LearningResource":
        return
    # Update cache for the LearningResource if it's already set.
    get_vocabs(instance.id)
    LearningResourceIndex().update_object(instance)
    # Update Elasticsearch index:
    from search.utils import index_resources
    index_resources([instance])


@statsd.timer('lore.elasticsearch.taxonomy_update')
@receiver(post_save)
def handle_resource_update(sender, **kwargs):
    """Update index when a LearningResource is updated."""
    if kwargs["created"]:
        # Don't index upon create; update only.
        return
    instance = kwargs.pop("instance")
    if instance.__class__.__name__ != "LearningResource":
        return
    from search.utils import index_resources
    index_resources([instance])


@statsd.timer('lore.elasticsearch.taxonomy_delete')
@receiver(post_delete)
def handle_resource_deletion(sender, **kwargs):
    """Delete index when instance is deleted."""
    instance = kwargs.pop("instance")
    if instance.__class__.__name__ != "LearningResource":
        return
    from search.utils import delete_index
    delete_index(instance)


@statsd.timer('lore.elasticsearch.taxonomy_create')
@receiver(post_save)
def handle_vocabulary_creation(sender, **kwargs):
    """Update index when a Vocabulary is created."""
    if not kwargs["created"]:
        # Only index upon create.
        return
    instance = kwargs.pop("instance")
    if instance.__class__.__name__ != "Vocabulary":
        return
    from learningresources.models import LearningResource
    from search.utils import index_resources
    index_resources(
        LearningResource.objects.filter(
            course__repository__id=instance.repository_id))
