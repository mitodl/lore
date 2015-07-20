"""
Import bits of the 'search' app which must be there when Django starts.
"""
from __future__ import unicode_literals

from haystack.query import SearchQuerySet

from search import signals
from taxonomy.models import Vocabulary


def get_sqs():
    """
    Get custom SearchQuerySet for LORE.

    Calling .facet() for every field must be done for the field
    to be in the "facets" context variable provided by Haystack.
    """
    sqs = SearchQuerySet()
    # Add hard-coded facets.
    for facet in ("course", "run", "resource_type"):
        sqs = sqs.facet(facet)
    # Add dynamic facets (from taxonomy). Values with spaces do not work,
    # so use the slug.
    for slug in Vocabulary.objects.all().values_list("slug", flat=True):
        sqs = sqs.facet(slug)
    return sqs
