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
    # Add dynamic facets (from taxonomy). Certain characters cause problems,
    # so use the primary key.
    for vocabulary_id in Vocabulary.objects.all().values_list("id", flat=True):
        sqs = sqs.facet(vocabulary_id)
    return sqs
