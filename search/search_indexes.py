"""
Index information for Haystack.

http://django-haystack.readthedocs.org/en/latest/tutorial.html
"""

from __future__ import unicode_literals

from haystack import indexes

from learningresources.models import LearningResource


class LearningResourceIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Index configuration for the LearningResource model.
    """
    text = indexes.CharField(document=True)
    resource_type = indexes.CharField(
        model_attr="learning_resource_type",
        faceted=True,
    )
    course = indexes.CharField(model_attr="course", faceted=True)
    run = indexes.CharField(model_attr="course", faceted=True)

    # repository is here for filtering the repository listing page by the
    # repo_slug in the URL. It is not used or needed in the repository listing
    # page because that page is always for a single repository.
    repository = indexes.CharField(faceted=True)

    def get_model(self):
        """Return the model for which this configures indexing."""
        return LearningResource

    def index_queryset(self, using=None):
        """Records to check when updating entire index."""
        return self.get_model().objects.all()

    def prepare_text(self, obj):  # pylint: disable=no-self-use
        """Indexing of the primary content of a LearningResource."""
        return "{0} {1} {2}".format(
            obj.title, obj.description, obj.content_xml,
        )

    def prepare_run(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "run" index."""
        return obj.course.run

    def prepare_course(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "course" index."""
        return obj.course.course_number

    def prepare_repository(self, obj):  # pylint: disable=no-self-use
        """Use the slug for the repo, since it's unique."""
        return obj.course.repository.slug
