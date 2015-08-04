"""
Index information for Haystack.

http://django-haystack.readthedocs.org/en/latest/tutorial.html

There are three ways to define what gets indexed for a field in
the index. They can not be mixed.

* Use the model_attr kwarg: This works when the field is text, or a
  foreign key to a model whose unicode representation is what we want.
* Use the use_template kwarg: For complex mixing of fields.
* Use a prepare_* function: Flexible and easy.
"""

from __future__ import unicode_literals

from collections import defaultdict
from datetime import datetime, timedelta
import logging

from django.conf import settings
from haystack import indexes
from lxml import etree

from learningresources.models import Course, LearningResource

INDEX_CACHE = {
    "course": {},
    "term": {},
    "born": datetime.now(),
}
MAX_INDEX_AGE = timedelta(minutes=1)

log = logging.getLogger(__name__)


def check_cache_age():
    """
    Keep the cache from getting stale.

    Must not cache during tests or development, or it will
    cause confusion. Must manually enable caching in production.
    """
    # pylint: disable=global-statement
    global INDEX_CACHE
    if (datetime.now() - INDEX_CACHE["born"] > MAX_INDEX_AGE) \
            or settings.ALLOW_CACHING is False:
        INDEX_CACHE = {
            "course": {},
            "term": {},
            "born": datetime.now(),
        }


def get_course_metadata(course_id):
    """
    Caches and returns course metadata.
    Args:
        course_id (int): Primary key of learningresources.models.Course
    Returns:
        data (dict): Metadata about course.
    """
    check_cache_age()
    data = INDEX_CACHE["course"].get(course_id, {})
    if data == {}:
        course = Course.objects.get(id=course_id)
        data["run"] = course.run
        data["course_number"] = course.course_number
        data["org"] = course.org
        data["repo_slug"] = course.repository.slug
        INDEX_CACHE["course"][course_id] = data
    return data


def get_vocabs(course_id, lid):
    """
    Caches and returns taxonomy metadata for a course.
    Args:
        course_id (int): Primary key of learningresources.models.Course
        lid (int): Primary key of learningresources.models.LearningResource
    Returns:
        data (dict): Vocab/term data for course.
    """
    check_cache_age()
    if INDEX_CACHE["term"].get(course_id) is None:
        INDEX_CACHE["term"][course_id] = defaultdict(lambda: defaultdict(list))
        rels = LearningResource.terms.related.through.objects.select_related(
            "term").filter(learningresource__course__id=course_id)
        for rel in rels.iterator():
            INDEX_CACHE["term"][course_id][rel.learningresource_id][
                rel.term.vocabulary_id].append(rel.term_id)
    return INDEX_CACHE["term"][course_id][lid]


class LearningResourceIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Index configuration for the LearningResource model.
    """
    text = indexes.CharField(document=True)
    resource_type = indexes.CharField(
        model_attr="learning_resource_type",
        faceted=True,
    )
    course = indexes.CharField(faceted=True)
    run = indexes.CharField(faceted=True)

    # repository is here for filtering the repository listing page by the
    # repo_slug in the URL. It is not used or needed in the repository listing
    # page because that page is always for a single repository.
    repository = indexes.CharField(faceted=True)

    nr_views = indexes.IntegerField(model_attr="xa_nr_views")
    nr_attempts = indexes.IntegerField(model_attr="xa_nr_attempts")
    avg_grade = indexes.FloatField(model_attr="xa_avg_grade")

    lid = indexes.IntegerField(model_attr="id", indexed=False)
    title = indexes.CharField(model_attr="title", indexed=False)
    description = indexes.CharField(model_attr="description", indexed=False)
    description_path = indexes.CharField(
        model_attr="description_path",
        indexed=False,
    )
    preview_url = indexes.CharField(indexed=False)

    def get_model(self):
        """Return the model for which this configures indexing."""
        return LearningResource

    def index_queryset(self, using=None):
        """Records to check when updating entire index."""
        return self.get_model().objects.all()

    def prepare_text(self, obj):  # pylint: disable=no-self-use
        """Indexing of the primary content of a LearningResource."""
        try:
            # Strip XML tags from content before indexing.
            tree = etree.fromstring(obj.content_xml)
            content = etree.tostring(tree, encoding="utf-8", method="text")
        except etree.XMLSyntaxError:
            # For blank/invalid XML.
            content = obj.content_xml
        try:
            content = content.decode('utf-8')
        except AttributeError:
            # For Python 3.
            pass

        return "{0} {1} {2}".format(
            obj.title, obj.description, content
        )

    def prepare_run(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "run" index."""
        data = get_course_metadata(obj.course_id)
        return data["run"]

    def prepare_preview_url(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "run" index."""
        data = get_course_metadata(obj.course_id)
        return obj.get_preview_url(
            org=data["org"],
            course_number=data["course_number"],
            run=data["run"],
        )

    @staticmethod
    def prepare_course(obj):
        """Define what goes into the "course" index."""
        data = get_course_metadata(obj.course_id)
        return data["course_number"]

    def prepare(self, obj):
        """
        Get dynamic vocabularies.

        The prepare() method runs last, similar to Django's form.clean().
        This allows us to override anything we want. Here we add vocabularies
        to the index because they must be dynamic.

        Technically, we could handle the other stuff (run, course, etc.) here
        as well, but don't because explicit is better than implicit.
        """
        prepared = super(LearningResourceIndex, self).prepare(obj)

        for vocab_id, term_ids in get_vocabs(obj.course_id, obj.id).items():
            # Use the integer primary keys as index values. This saves space,
            # and also avoids all issues dealing with "special" characters.
            prepared[vocab_id] = term_ids
            # For faceted "_exact" in URL.
            prepared["{0}_exact".format(vocab_id)] = term_ids
        return prepared

    def prepare_repository(self, obj):  # pylint: disable=no-self-use
        """Use the slug for the repo, since it's unique."""
        data = get_course_metadata(obj.course_id)
        return data["repo_slug"]
