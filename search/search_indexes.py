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

from lxml import etree
from haystack import indexes

from learningresources.models import LearningResource
from taxonomy.models import Vocabulary


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
        return obj.course.run

    @staticmethod
    def prepare_course(obj):
        """Define what goes into the "course" index."""
        return obj.course.course_number

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
        for vocab in Vocabulary.objects.all():
            # Values with spaces do not work, so replace them with underscores.
            # Slugify doesn't work because it adds hypens, which are also
            # split by Elasticsearch.
            terms = [
                term.label.replace(" ", "_")
                for term in obj.terms.filter(vocabulary_id=vocab.id)
            ]
            prepared[vocab.slug] = terms
            # for faceted "_exact" in URL
            prepared[vocab.slug + "_exact"] = terms  # for faceted "exact"
        return prepared

    def prepare_repository(self, obj):  # pylint: disable=no-self-use
        """Use the slug for the repo, since it's unique."""
        return obj.course.repository.slug
