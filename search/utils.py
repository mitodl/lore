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
from elasticsearch_dsl import Search, Mapping, query
from elasticsearch_dsl.connections import connections

from statsd.defaults.django import statsd

from learningresources.models import get_preview_url, LearningResource
from search.search_indexes import get_course_metadata
from search.tasks import refresh_index as _refresh_index
from taxonomy.models import Vocabulary

log = logging.getLogger(__name__)

DOC_TYPE = "learningresource"
INDEX_NAME = settings.HAYSTACK_CONNECTIONS["default"]["INDEX_NAME"]
URL = settings.HAYSTACK_CONNECTIONS["default"]["URL"]
_CONN = None
PAGE_LENGTH = 10


def get_vocab_names():
    """Get all vocabulary names in the database."""
    return Vocabulary.objects.all().values_list('name', flat=True)


def get_conn():
    """
    Lazily create the connection.

    Upon creating the connection, create the index if necessary.
    """
    # pylint: disable=global-statement
    # This is ugly. Any suggestions on a way that doesn't require "global"?
    global _CONN
    if _CONN is None:
        _CONN = connections.create_connection(hosts=[URL])

    # Make sure everything exists.
    if not _CONN.indices.exists(INDEX_NAME):
        _CONN.indices.create(INDEX_NAME)

    mappings = _CONN.indices.get_mapping()[INDEX_NAME]["mappings"]
    if DOC_TYPE not in mappings.keys():
        _create_mapping()
    return _CONN


def get_resource_terms(resource_ids):
    """
    Returns taxonomy metadata for LearningResources.
    Args:
        resource_ids (iterable of int): Primary keys of LearningResources
    Returns:
        data (dict): Vocab/term data for course.
    """
    vocab_names = get_vocab_names()
    resource_data = defaultdict(lambda: defaultdict(list))
    rels = LearningResource.terms.related.through.objects.select_related(
        "term__vocabulary").filter(learningresource__id__in=resource_ids)
    for rel in rels.iterator():
        obj = resource_data[rel.learningresource_id]
        obj[rel.term.vocabulary.name].append(rel.term.label)
    # Replace the defaultdicts with dicts.
    info = {k: dict(v) for k, v in resource_data.items()}
    for resource_id in resource_ids:
        if resource_id not in info.keys():
            info[resource_id] = {}
        for vocab_name in vocab_names:
            if vocab_name not in info[resource_id].keys():
                info[resource_id][vocab_name] = [None]
    return info


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
        search = Search(index=INDEX_NAME, doc_type=DOC_TYPE)
    else:
        # Search on title, description, and content_xml (minus markup).
        search = Search(index=INDEX_NAME, doc_type=DOC_TYPE)
        multi = query.MultiMatch(
            query=tokens, fields=["title", "description", "content_stripped"])
        search = search.query(multi)

    # Filter further on taxonomy terms.
    for key, value in terms.items():
        search = search.query("match", **{key: value})

    if repo_slug is not None:
        # Filter further on repository.
        search = search.query("match", repository=repo_slug)
    if sort_by is None:
        # Always sort by ID to preserve ordering.
        search = search.sort("id")
    else:
        # Temporary workaround; the values in sorting.py should be updated,
        # but for now Haystack is still using them. Also, the hyphen is
        # required because we sort the numeric values high to low.
        if "title" not in sort_by:
            reverse = sort_by.startswith("-")
            if reverse:
                sort_by = sort_by[1:]
            if "xa" not in sort_by:
                sort_by = "xa_{0}".format(sort_by)
            if reverse:
                sort_by = "-{0}".format(sort_by)
        # Always sort by ID to preserve ordering.
        search = search.sort(sort_by, "id")

    terms = set(get_vocab_names())
    terms.update(set(('run', 'course', 'resource_type')))
    for term in terms:
        search.aggs.bucket(term, "terms", field=term)

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
        (resource_to_dict(x, term_info[x.id]) for x in resources),
        index=INDEX_NAME,
        doc_type=DOC_TYPE,
    )

    if errors != []:
        log.error("Error during bulk insert: %s", errors)
    refresh_index()

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


def resource_to_dict(resource, term_info):
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

    rec = {
        "title": resource.title,
        # The zero is for sorting blank items to the bottom. See below.
        "titlesort": "0{0}".format(resource.title.strip()),
        "id": resource.id,
        "_id": resource.id,  # The ID used by Elasticsearch.
        "resource_type": resource.learning_resource_type.name,
        "description": resource.description,
        "description_path": resource.description_path,
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
        'content_stripped', 'description_path',
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
        get_conn()  # We don't need the return value; just for it to exist.

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

    def aggregations(self):
        """Return aggregations."""
        return convert_aggregate(vars(self._search.execute().aggregations))

    def __getitem__(self, i):
        """Return result by index."""
        if isinstance(i, slice):
            return self._search[i].execute().hits
        else:
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
    get_conn()


def _create_mapping():
    """
    Actually create the mapping, including deleting it if it's there
    so we can create it.
    """
    # Delete the mapping if an older version exists.
    if _CONN.indices.exists_type(index=INDEX_NAME, doc_type=DOC_TYPE):
        _CONN.indices.delete_mapping(index=INDEX_NAME, doc_type=DOC_TYPE)

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
    mapping.field("titlesort", "string", index="not_analyzed")
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
    _CONN.indices.refresh()


def refresh_index():
    """
    Force a refresh instead of waiting for it to happen automatically.
    This should only be necessary during tests.

    When this was switched to use Celery,
    _refresh_index() was created instead of just updating all existing calls
    to refresh_index() to call .delay() because that makes it easy to add any
    code that needs to call refresh_index in the future being aware of Celery.
    """
    get_conn()
    _refresh_index.delay(INDEX_NAME)


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

    get_conn()  # We don't need the return value; just for it to exist.

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
        refresh_index()


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


def convert_aggregate(agg):
    """
    Convert elasticsearch-dsl output to the facet output
    currently being created from the Haystack data.
    Args:
        agg: Agg
    Returns:
        updated (dict): facet data
    """

    def format_key(key):
        """Custom conversions for build-in facets."""
        table = {
            'run': 'Run',
            'course': 'Course',
            'resource_type': 'Item Type',
        }
        return table.get(key, key)

    missing_counts = {}
    updated = agg['_d_']
    for key in updated.keys():
        updated[key]["facet"] = updated[key]["buckets"]
        del updated[key]["buckets"]
        del updated[key]["doc_count_error_upper_bound"]
        del updated[key]["sum_other_doc_count"]
        temp_values = updated[key]["facet"]
        updated[key]["values"] = []
        for rec in temp_values:
            # We have the empty values as part of the aggregation, unlike
            # in Haystack. We have to pull them out specially to present
            # the data the same way Haystack did.
            if rec["key"] == "empty":
                missing_counts[key] = rec["doc_count"]
                continue
            rec["count"] = rec["doc_count"]
            rec["label"] = rec["key"]
            del rec["doc_count"]
            updated[key]["values"].append(rec)

    for facet in updated.keys():
        updated[facet]["facet"] = {
            "key": facet,
            "label": format_key(facet),
            "missing_count": missing_counts.get(facet, 0),
        }
    return updated
