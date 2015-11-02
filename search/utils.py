"""
Search functions.
"""

from __future__ import unicode_literals

from collections import defaultdict
from lxml import etree
import logging
from itertools import islice

from django.conf import settings
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search, Mapping, query
from elasticsearch_dsl.connections import connections

from statsd.defaults.django import statsd

from learningresources.models import get_preview_url, LearningResource
from rest.serializers import RepositorySearchSerializer
from search.exceptions import ReindexException
from search.search_indexes import get_course_metadata
from search.tasks import refresh_index as _refresh_index
from taxonomy.models import Vocabulary, Term, make_vocab_key

log = logging.getLogger(__name__)

DOC_TYPE = "learningresource"
INDEX_NAME = settings.HAYSTACK_CONNECTIONS["default"]["INDEX_NAME"]
URL = settings.HAYSTACK_CONNECTIONS["default"]["URL"]
_CONN = None
_CONN_VERIFIED = False
PAGE_LENGTH = 10


def get_vocab_ids(repo_slug=None):
    """Get all vocabulary names in the database."""
    if repo_slug is not None:
        return Vocabulary.objects.filter(
            repository__slug=repo_slug).values_list('id', flat=True)
    else:
        return Vocabulary.objects.all().values_list('id', flat=True)


def get_conn(verify=True):
    """
    Lazily create the connection.
    """
    # pylint: disable=global-statement
    # This is ugly. Any suggestions on a way that doesn't require "global"?
    global _CONN
    global _CONN_VERIFIED

    do_verify = False
    if _CONN is None:
        _CONN = connections.create_connection(hosts=[URL])
        # Verify connection on first connect if verify=True.
        do_verify = verify

    if verify and not _CONN_VERIFIED:
        # If we have a connection but haven't verified before, do it now.
        do_verify = True

    if not do_verify:
        if not verify:
            # We only skip verification if we're reindexing or
            # deleting the index. Make sure we verify next time we connect.
            _CONN_VERIFIED = False
        return _CONN

    # Make sure everything exists.
    if not _CONN.indices.exists(INDEX_NAME):
        raise ReindexException("Unable to find index {index_name}".format(
            index_name=INDEX_NAME
        ))

    mapping = _CONN.indices.get_mapping()
    if INDEX_NAME not in mapping:
        raise ReindexException(
            "No mappings found in index {index_name}".format(
                index_name=INDEX_NAME
            )
        )

    mappings = _CONN.indices.get_mapping()[INDEX_NAME]["mappings"]
    if DOC_TYPE not in mappings.keys():
        raise ReindexException("Mapping {doc_type} not found".format(
            doc_type=DOC_TYPE
        ))

    _CONN_VERIFIED = True
    return _CONN


def get_resource_terms(resource_ids):
    """
    Returns taxonomy metadata for LearningResources.
    Args:
        resource_ids (iterable of int): Primary keys of LearningResources
    Returns:
        data (dict): Vocab/term ids for course.
    """
    vocab_ids = get_vocab_ids()
    resource_data = defaultdict(lambda: defaultdict(list))
    rels = LearningResource.terms.related.through.objects.select_related(
        "term__vocabulary").filter(learningresource__id__in=resource_ids)
    for rel in rels.iterator():
        obj = resource_data[rel.learningresource_id]
        obj[rel.term.vocabulary.id].append(rel.term.id)
    # Replace the defaultdicts with dicts.
    info = {k: dict(v) for k, v in resource_data.items()}
    for resource_id in resource_ids:
        if resource_id not in info.keys():
            info[resource_id] = {}
        for vocab_id in vocab_ids:
            if vocab_id not in info[resource_id].keys():
                info[resource_id][vocab_id] = []
    return info


def _get_field_names():
    """Return list of search field names."""
    return list(
        RepositorySearchSerializer.get_fields(RepositorySearchSerializer()))


# pylint: disable=too-many-branches
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

    search = Search(index=INDEX_NAME, doc_type=DOC_TYPE)

    # Limit returned fields since content_xml can be huge and is unnecessary.
    search = search.fields(_get_field_names())

    if tokens is not None:
        # Search on title, description, and content_xml (minus markup).
        multi = query.MultiMatch(
            query=tokens, fields=["title", "description", "content_stripped"])
        search = search.query(multi)

    # Filter further on taxonomy terms.
    for key, value in terms.items():
        if value is None:
            search = search.query(
                "query_string",
                query="_missing_:({key})".format(key=key)
            )
        else:
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

    vocab_ids = set(get_vocab_ids(repo_slug=repo_slug))
    for vocab_id in vocab_ids:
        vocab_key = make_vocab_key(vocab_id)
        search.aggs.bucket(
            "{key}_missing".format(key=vocab_key),
            "missing", field=vocab_key
        )
        search.aggs.bucket(
            "{key}_buckets".format(key=vocab_key),
            "terms", field=vocab_key
        )
    for key in ('run', 'course', 'resource_type'):
        search.aggs.bucket(
            '{key}_builtins'.format(key=key), "terms", field=key
        )

    return SearchResults(search)


@statsd.timer('lore.elasticsearch.bulk_index_chunk')
def _index_resource_chunk(resource_ids):
    """Add/update records in Elasticsearch."""

    # Terms assigned to the resources.
    term_info = get_resource_terms(resource_ids)

    ensure_vocabulary_mappings(term_info)

    # Perform bulk insert using Elasticsearch directly.
    conn = get_conn()
    resources = LearningResource.objects.filter(id__in=resource_ids).iterator()
    insert_count, errors = bulk(
        conn,
        (resource_to_dict(x, term_info[x.id]) for x in resources),
        index=INDEX_NAME,
        doc_type=DOC_TYPE,
    )

    if errors != []:
        raise ReindexException("Error during bulk insert: {errors}".format(
            errors=errors
        ))
    refresh_index()

    return insert_count


@statsd.timer('lore.elasticsearch.bulk_index')
def index_resources(resource_ids, chunk_size=100):
    """Add/update records in Elasticsearch."""

    # Must be an iterator so islice doesn't pull the same n items each
    # time.
    resource_ids = iter(resource_ids)

    # Limit chunk size to 100 to avoid storing it all
    # in memory at once.
    chunk = list(islice(resource_ids, chunk_size))
    while len(chunk) > 0:
        _index_resource_chunk(chunk)
        chunk = list(islice(resource_ids, chunk_size))

    refresh_index()


@statsd.timer('lore.elasticsearch.delete_index')
def delete_resource_from_index(resource):
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
    for vocab_id, term_ids in term_info.items():
        rec[make_vocab_key(vocab_id)] = term_ids

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


def remove_index():
    """
    Delete the index.
    """
    conn = get_conn(verify=False)
    if conn.indices.exists(INDEX_NAME):
        conn.indices.delete(INDEX_NAME)


def recreate_index():
    """Wipe and recreate index and mapping, and index all resources."""
    conn = get_conn(verify=False)
    remove_index()
    conn.indices.create(INDEX_NAME)
    conn.indices.refresh()

    create_mapping()

    # re-index all existing LearningResource instances:
    index_resources(LearningResource.objects.values_list("id", flat=True))


class SearchResults(object):
    """
    Helper class for elasticsearch_dsl search results.

    This is because the actual search result has nested types, which
    would be cumbersome to access from arbitrary calling functions.
    """
    def __init__(self, search):
        """Get raw search result from Elasticsearch."""
        self._search = search
        self._cached_agg = None
        self._cached_count = None
        get_conn()  # We don't need the return value; just for it to exist.

    def count(self):
        """Total records matching the query."""
        if self._cached_count is None:
            self._cached_count = self._search.count()
        return self._cached_count

    def page_count(self):
        """Total number of result pages."""
        total = self.count()
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
        if self._cached_agg is None:
            self._cached_agg = self._search.params(
                search_type="count").execute()
        return convert_aggregate(vars(self._cached_agg.aggregations))

    def __getitem__(self, i):
        """Return result by index."""
        if isinstance(i, slice):
            hits = self._search[i].execute().hits
        else:
            hits = self._search[slice(i, i+1)].execute().hits

        for hit in hits:
            for field_name in _get_field_names():
                setattr(hit, field_name, getattr(hit, field_name)[0])

        if isinstance(i, slice):
            return hits
        else:
            return hits[0]


def create_mapping():
    """
    Delete and recreate the Elasticsearch mapping.

    Notes on the "index" values:
        analyzed: normal, will be split on whitespace for indexing
            (partial matches can be made during queries)
        not_analyzed: no split; matches must be exact
        no: not indexed at all, but will be returned in search results
    """
    conn = get_conn(verify=False)
    _create_mapping(conn)


def _create_mapping(conn):
    """
    Actually create the mapping, including deleting it if it's there
    so we can create it.
    """

    # Delete the mapping if an older version exists.

    if conn.indices.exists_type(index=INDEX_NAME, doc_type=DOC_TYPE):
        conn.indices.delete_mapping(index=INDEX_NAME, doc_type=DOC_TYPE)

    mapping = Mapping(DOC_TYPE)
    mapping.field("id", "integer")
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
    vocab_ids = set()
    for vocab_terms in term_info.values():
        for vocab_id in vocab_terms.keys():
            vocab_ids.add(vocab_id)
    updated = False
    # Add vocabulary to mapping if necessary.
    for vocab_id in vocab_ids:
        vocab_key = make_vocab_key(vocab_id)
        if vocab_key in existing_vocabs:
            continue
        mapping.field(vocab_key, "string", index="not_analyzed")
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


# pylint: disable=too-many-locals
def convert_aggregate(agg):
    """
    Convert elasticsearch-dsl output to the facet output
    currently being created from the Haystack data.
    Args:
        agg: Agg
    Returns:
        reformatted (dict): facet data
    """

    special_labels = {
        'run': 'Run',
        'course': 'Course',
        'resource_type': 'Item Type',
    }

    vocab_lookup = {}
    term_lookup = {}
    for term in Term.objects.all():
        term_lookup[term.id] = term.label

    for vocab in Vocabulary.objects.all():
        vocab_lookup[make_vocab_key(vocab.id)] = vocab.name

    def get_vocab_label(vocab_key):
        """Get label for vocab."""
        return vocab_lookup.get(vocab_key, vocab_key)

    def get_term_label(term_id):
        """Get label for term."""
        return term_lookup.get(int(term_id), str(term_id))

    def get_builtin_label(key):
        """Get label for special types."""
        return special_labels.get(key, key)

    # Group into fields.
    vocab_buckets = defaultdict(dict)
    builtin_buckets = defaultdict(dict)
    for key, value in agg['_d_'].items():
        if key.endswith("_missing"):
            key = key[:-len("_missing")]
            vocab_buckets[key]['missing'] = value
        elif key.endswith("_buckets"):
            key = key[:-len("_buckets")]
            vocab_buckets[key]['buckets'] = value['buckets']
        elif key.endswith("_builtins"):
            key = key[:-len("_builtins")]
            builtin_buckets[key]['buckets'] = value['buckets']
            # No missing counts for run, course, resource_types.

    reformatted = {}
    for key, buckets_and_missing in vocab_buckets.items():
        buckets = buckets_and_missing['buckets']
        missing = buckets_and_missing['missing']

        values = [
            {
                "key": facet['key'],
                "label": get_term_label(facet['key']),
                "count": facet["doc_count"]
            } for facet in buckets
        ]
        facet = {
            "key": key,
            "label": get_vocab_label(key),
            'missing_count': missing['doc_count']
        }

        reformatted[key] = {
            "facet": facet,
            "values": values,
        }

    for key, buckets_and_missing in builtin_buckets.items():
        buckets = buckets_and_missing['buckets']

        values = [
            {
                "key": facet['key'],
                "label": facet['key'],
                "count": facet['doc_count']
            } for facet in buckets
        ]
        facet = {
            "key": key,
            "label": get_builtin_label(key),
            "missing_count": 0
        }

        reformatted[key] = {
            "facet": facet,
            "values": values,
        }

    return reformatted
