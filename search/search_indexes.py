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
import logging

from django.core.cache import caches

from learningresources.models import Course, LearningResource

log = logging.getLogger(__name__)

cache = caches["lore_indexing"]


def get_course_metadata(course_id):
    """
    Caches and returns course metadata.
    Args:
        course_id (int): Primary key of learningresources.models.Course
    Returns:
        data (dict): Metadata about course.
    """
    key = "course_metadata_{0}".format(course_id)
    data = cache.get(key, {})
    if data == {}:
        course = Course.objects.select_related("repository").get(id=course_id)
        data["run"] = course.run
        data["course_number"] = course.course_number
        data["org"] = course.org
        data["repo_slug"] = course.repository.slug
        cache.set(key, data)
    # Return `data` directly, not from the cache. Otherwise, if caching
    # is disabled (TIMEOUT == 0), this will always return nothing.
    return data


def get_vocabs(resource_id):
    """
    Returns taxonomy metadata for a course.
    Args:
        resource_id (int): Primary key of LearningResource
    Returns:
        data (dict): Vocab/term data for course.
    """
    data = defaultdict(list)
    rels = LearningResource.terms.related.through.objects.select_related(
        "term").filter(learningresource__id=resource_id)
    for rel in rels.iterator():
        data[rel.term.vocabulary_id].append(rel.term_id)
    return dict(data)
