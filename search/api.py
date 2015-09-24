"""
Functions for search functionality.
"""

from __future__ import unicode_literals

from haystack.query import SearchQuerySet

from search.sorting import LoreSortingFields
from search.utils import search_index
from taxonomy.models import Vocabulary, Term
from ui.views import get_vocabularies


def construct_queryset(repo_slug, query='', selected_facets=None, sortby=''):
    """
    Create a SearchQuerySet given search parameters.

    Args:
        repo_slug (learningresources.models.Repository):
            Slug for repository being searched.
        query (unicode): If present, search phrase to use in queryset.
        selected_facets (list or None):
            If present, a list of facets to narrow the search with.
        sortby (unicode): If present, order by this sorting option.
    Returns:
        search.utils/SearchResults: The search results.
    """

    if selected_facets is None:
        selected_facets = []

    queryset = SearchQuerySet()

    kwargs = {}
    for facet in selected_facets:
        queryset = queryset.narrow(facet)

    if query != "":
        kwargs["content"] = query

    queryset = queryset.filter(**kwargs)

    queryset = queryset.narrow("repository_exact:{slug}".format(
        slug=repo_slug))

    if sortby == "":
        sortby = LoreSortingFields.DEFAULT_SORTING_FIELD
    # default values in case of weird sorting options
    sortby, _, order_direction = LoreSortingFields.get_sorting_option(
        sortby)
    sortby = "{0}{1}".format(order_direction, sortby)
    queryset = queryset.order_by(
        sortby, LoreSortingFields.BASE_SORTING_FIELD)

    # Do a parallel query using elasticsearch-dsl.
    if query not in ("", None):
        tokens = query
    else:
        tokens = None
    terms = {}
    for facet in selected_facets:
        key, value = facet.split(":")

        # Haystack queries for blanks by putting the key last, as the value,
        # and setting the key to "_missing_." Fix  this for elasticsearch-dsl.
        if key == '_missing_':
            key, value = value, "empty"

        if key.endswith("_exact"):
            key = key[:-6]

        # Look for facets
        if key.isdigit():
            key = get_vocab_name(key)
            if value is not 'empty':
                value = get_term_label(value)
        terms[key] = value

    # This is sneakily being returned instead of the
    # Haystack queryset created above.
    results = search_index(
        tokens=tokens,
        repo_slug=repo_slug,
        sort_by=sortby,
        terms=terms,
    )

    return results


def make_facet_counts(repo_slug, queryset):
    """
    Facets on every facet available and provides a data structure
    of facet count information ready for API use.

    Args:
        repo_slug (unicode): The slug for the repository.
        queryset (haystack.query.SearchQuerySet):
            The queryset to use for counting facets.
    Returns:
        dict:
            A data structure with facet count information. It's structured
            like this:
            {"resource_type": {
                "facet": {"key": "resource_type", "label": "Item Type"},
                "values": [
                    {"count": 39, "key": "vertical", "label": "vertical"}
                    ...

    """

    def reformat(key, values, missing_count=None):
        """Convert tuples to dictionaries so we can use keys."""
        reformatted = {
            "facet": {
                "key": str(key[0]),
                "label": key[1]
            },
            "values": [
                {
                    "label": value_label,
                    "key": str(value_key),
                    "count": count
                } for value_key, value_label, count in values
            ]
        }
        if missing_count is not None:
            reformatted["facet"]["missing_count"] = missing_count
        return reformatted

    for facet in ('course', 'run', 'resource_type'):
        queryset = queryset.facet(facet)

    vocabularies = Vocabulary.objects.filter(repository__slug=repo_slug)

    for vocabulary in vocabularies:
        queryset = queryset.facet(vocabulary.id)

    facet_counts = queryset.facet_counts()
    vocabs = get_vocabularies(facet_counts)

    # return dictionary
    ret_dict = {}

    # process vocabularies
    for key, values in vocabs.items():
        missing_count = queryset.filter(
            _missing_='{0}_exact'.format(key[0])).count()
        ret_dict[key[0]] = reformat(
            key, values, missing_count=missing_count)

    # Reformat facet_counts to match term counts.
    for key, label in (
            ("course", "Course"),
            ("run", "Run"),
            ("resource_type", "Item Type")
    ):
        if 'fields' in facet_counts:
            values = [(name, name, count) for name, count
                      in facet_counts['fields'][key]]
        else:
            values = []
        ret_dict[key] = reformat((key, label), values)

    return ret_dict


def get_vocab_name(vocab_id):
    """Get vocabulary name by ID."""
    vocab = Vocabulary.objects.get(id=vocab_id)
    return vocab.name


def get_term_label(term_id):
    """Get term label by ID."""
    return Term.objects.get(id=term_id).label
