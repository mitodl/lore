"""
Search functions.
"""

from __future__ import unicode_literals

from collections import defaultdict
from lxml import etree
import logging

from django.conf import settings
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search, Mapping, query

from statsd.defaults.django import statsd

from learningresources.models import get_preview_url, LearningResource
from search.search_indexes import get_course_metadata

log = logging.getLogger(__name__)

DOC_TYPE = "learningresource"
INDEX_NAME = settings.HAYSTACK_CONNECTIONS["default"]["INDEX_NAME"]
URL = settings.HAYSTACK_CONNECTIONS["default"]["URL"]
_CONN = None
PAGE_LENGTH = 10


def get_conn():
    """
    Lazily create the connection.
    """
    # pylint: disable=global-statement
    # This is ugly. Any suggestions on a way that doesn't require "global"?
    global _CONN
    if _CONN is None:
        _CONN = connections.create_connection(hosts=[URL])
    return _CONN


def get_resource_terms(resource_ids):
    """
    Returns taxonomy metadata for LearningResources.
    Args:
        resource_ids (iterable of int): Primary keys of LearningResources
    Returns:
        data (dict): Vocab/term data for course.
    """
    resource_data = defaultdict(lambda: defaultdict(list))
    rels = LearningResource.terms.related.through.objects.select_related(
        "term__vocabulary").filter(learningresource__id__in=resource_ids)
    for rel in rels.iterator():
        obj = resource_data[rel.learningresource_id]
        obj[rel.term.vocabulary.name].append(rel.term.label)
    # Replace the defaultdicts with dicts.
    return {k: dict(v) for k, v in resource_data.items()}


def search_index(tokens=None, repo_slug=None, sort_by=None, terms=None):
    """
    Perform a search in Elasticsearch.

    Args:
        tokens (unicode): string of one or more words
        repo_slug (unicode): repository slug
        sort_by (string): field to sort by
        terms: (dict): {"vocabulary name": ["term1" [, "term2"]]}
    Returns:
        results (SearchResults)
    """
    if terms is None:
        terms = {}
    if tokens is None:
        # Retrieve everything.
        search = Search(index=INDEX_NAME, doc_type=DOC_TYPE).query()
    else:
        # Search on title, description, and content_xml (minus markup).
        search = Search(index=INDEX_NAME, doc_type=DOC_TYPE)
        multi = query.MultiMatch(
            query=tokens, fields=["title", "description", "content_stripped"])
        search = search.query(multi)
    if terms != {}:
        # Filter further on taxonomy terms.
        search = search.query("match", **terms)
    if repo_slug is not None:
        # Filter further on repository.
        search = search.query("match", repository=repo_slug)
    if sort_by is not None:
        # Temporary workaround; the values in sorting.py should be updated,
        # but for now Haystack is still using them. Also, the hyphen is
        # required because we sort the numeric values high to low.
        if not sort_by.startswith("title"):
            sort_by = "-xa_{0}".format(sort_by)
        search = search.sort(sort_by, "id")
    return SearchResults(search)


@statsd.timer('lore.elasticsearch.bulk_index')
def index_resources(resources):
    """Add/update records in Elasticsearch."""

    if hasattr(resources, "values_list"):
        # If it's a queryset, get the IDs the smart way.
        resource_ids = resources.values_list("id", flat=True)
    else:
        resource_ids = [x.id for x in resources]
    # Terms assigned to the resources.
    term_info = get_resource_terms(resource_ids)

    if hasattr(resources, "iterator"):
        # If it's a queryset, be efficient.
        resources = resources.iterator()

    ensure_vocabulary_mappings(term_info)

    # Perform bulk insert using Elasticsearch directly.
    conn = get_conn()
    insert_count, errors = bulk(
        conn,
        (resource_to_dict(x, term_info.get(x.id, {})) for x in resources),
        index=INDEX_NAME,
        doc_type=DOC_TYPE
    )

    if errors != []:
        log.error("Error during bulk insert: %s", errors)

    return insert_count


@statsd.timer('lore.elasticsearch.delete_index')
def delete_index(resource):
    """Delete a record from Elasticsearch."""
    conn = get_conn()
    try:
        conn.delete(
            index=INDEX_NAME, doc_type=DOC_TYPE, id=resource.id)
        refresh_index()
    except NotFoundError:
        # We tried to delete something that wasn't in the index.
        # In that case, we don't care; the desired outcome is identical.
        pass


def resource_to_dict(resource, term_info=None):
    """
    Retrieve important values from a LearningResource to index.

    This dict corresponds to the mapping created in Elasticsearch.

    The titlesort bits, with the "0" and "1" prefixes, were copied from
    the prepare_titlesort function in search/search_indexes.py. It was there
    to make blank titles sort to the bottom instead of the top.

    Args:
        resource (LearningResource): Item to convert to dict.
        term_info (dict): Vocabulary terms assigned to resource.
    Returns:
        rec (dict): Dictionary representation of the LearningResource.
    """

    if term_info is None:
        term_info = {}
    rec = {
        "title": resource.title,
        # The zero is for sorting blank items to the bottom. See below.
        "titlesort": "0{0}".format(resource.title.strip()),
        "id": resource.id,
        "_id": resource.id,  # The ID used by Elasticsearch.
        "resource_type": resource.learning_resource_type.name,
        "description": resource.description,
        "content_xml": resource.content_xml,
        "content_stripped": strip_xml(resource.content_xml),
        "xa_nr_views": resource.xa_nr_views,
        "xa_nr_attempts": resource.xa_nr_attempts,
        "xa_avg_grade": resource.xa_avg_grade,
        "xa_histogram_grade": resource.xa_histogram_grade,
    }

    course = get_course_metadata(resource.course_id)
    rec["preview_url"] = get_preview_url(
        resource,
        org=course["org"],
        course_number=course["course_number"],
        run=course["run"],
    )
    rec["run"] = course["run"]
    rec["course"] = course["course_number"]
    rec["repository"] = course["repo_slug"]

    # Index term info. Since these fields all use the "not_analyzed"
    # index, they must all be exact matches.
    for key, vals in term_info.items():
        rec[key] = vals

    # If the title is empty, sort it to the bottom. See above.
    if rec["titlesort"] == "0":
        rec["titlesort"] = "1"

    # Keys that may have unicode issues.
    text_keys = (
        'title', 'titlesort', 'resource_type', 'description', 'content_xml',
        'content_stripped',
    )
    for key in text_keys:
        try:
            # Thanks to unicode_literals above, this works in
            # Python 2 and Python 3. Avoid trying to decode a string
            # if it's already unicode.
            if not isinstance(rec[key], type("")):
                rec[key] = rec[key].decode('utf-8')
        except AttributeError:
            pass  # Python 3
    return rec


def clear_index():
    """Wipe the index."""
    conn = get_conn()
    if conn.indices.exists(INDEX_NAME):
        conn.indices.delete(INDEX_NAME)
        conn.indices.create(INDEX_NAME)
        conn.indices.refresh()
    create_mapping()

    # re-index all existing LearningResource instances:
    index_resources(LearningResource.objects.all())


class SearchResults(object):
    """
    Helper class for elasticsearch_dsl search results.

    This is because the actual search result has nested types, which
    would be cumbersome to access from arbitrary calling functions.
    """
    def __init__(self, search):
        """Get raw search result from Elasticsearch."""
        self._search = search

    def count(self):
        """Total records matching the query."""
        return self._search.count()

    def page_count(self):
        """Total number of result pages."""
        total = self._search.count()
        count = total / PAGE_LENGTH
        if total % PAGE_LENGTH > 0:
            count += 1
        return int(count)

    def get_page(self, page):
        """Return paginated results."""
        start = (page - 1) * PAGE_LENGTH
        end = start + PAGE_LENGTH
        return self._search[start:end].execute().hits

    def all(self):
        """Return all results in a generator."""
        for i in range(self.page_count()):
            for hit in self.get_page(i+1):
                yield hit

    def __getitem__(self, i):
        """Return result by index."""
        return self._search[i].execute().hits[0]


def create_mapping():
    """
    Create the Elasticsearch mapping.

    Notes on the "index" values:
        analyzed: normal, will be split on whitespace for indexing
            (partial matches can be made during queries)
        not_analyzed: no split; matches must be exact
        no: not indexed at all, but will be returned in search results
    """

    # Create the index if it doesn't exist.
    conn = get_conn()
    if not conn.indices.exists(INDEX_NAME):
        conn.indices.create(INDEX_NAME)
    # Delete the mapping if an older version exists.
    if conn.indices.exists_type(index=INDEX_NAME, doc_type=DOC_TYPE):
        conn.indices.delete_mapping(index=INDEX_NAME, doc_type=DOC_TYPE)

    mapping = Mapping(DOC_TYPE)

    mapping.field("course", "string", index="not_analyzed")
    mapping.field("description_path", "string", index="no")
    mapping.field("description", "string", index="analyzed")
    mapping.field("preview_url", "string", index="no")
    mapping.field("repository", "string", index="not_analyzed")
    mapping.field("resource_type", "string", index="not_analyzed")
    mapping.field("content_xml", "string", index="no")
    mapping.field("content_stripped", "string", index="analyzed")
    mapping.field("run", "string", index="not_analyzed")
    mapping.field("titlesort", "string", index="no")
    mapping.field("title", "string", index="analyzed")

    mapping.field("xa_avg_grade", "float")
    mapping.field("xa_histogram_grade", "float")
    mapping.field("xa_nr_attempts", "integer")
    mapping.field("xa_nr_views", "integer")

    mapping.save(INDEX_NAME)

    # If we've done this, we always want to re-index all existing
    # LearningResource instances. This function will probably only
    # ever be called by migrations.
    index_resources(LearningResource.objects.all())
    conn.indices.refresh()


def refresh_index():
    """
    Force a refresh instead of waiting for it to happen automatically.
    This should only be necessary during tests.
    """
    conn = get_conn()
    conn.indices.refresh(index=INDEX_NAME)


def ensure_vocabulary_mappings(term_info):
    """
    Ensure the mapping is properly set in Elasticsearch to always do exact
    matches on taxonomy terms. Accepts the output of get_resource_terms.

    Calling this function during indexing means that vocabularies do not
    need to be added to the mapping in advance. This deals with the fact
    that vocabularies can be added on-the-fly without having to play around
    with extra signals.

    Args:
        term_info (dict): Details of terms for a group of LearningResources.
    """
    if len(term_info) == 0:
        return

    # Retrieve current mapping from Elasticsearch.
    mapping = Mapping.from_es(index=INDEX_NAME, doc_type=DOC_TYPE)

    # Get the field names from the mapping.
    existing_vocabs = set(mapping.to_dict()["learningresource"]["properties"])

    # Get all the taxonomy names from the data.
    vocab_names = set()
    for result in term_info.values():
        for key in result.keys():
            vocab_names.add(key)
    updated = False
    # Add vocabulary to mapping if necessary.
    for name in vocab_names:
        if name in existing_vocabs:
            continue
        mapping.field(name, "string", index="not_analyzed", null_value="empty")
        updated = True
    if updated:
        mapping.save(INDEX_NAME)


def strip_xml(content):
    """
    Strip XML from a string.
    Args:
        content (unicode): some XML
    Returns:
        output (unicode): plain text
    """
    try:
        # Strip XML tags from content before indexing.
        tree = etree.fromstring(content)
        content = etree.tostring(tree, encoding="utf-8", method="text")
    except etree.XMLSyntaxError:
        # For blank/invalid XML.
        pass
    try:
        content = content.decode('utf-8')
    except AttributeError:
        # For Python 3.
        pass

    return content
