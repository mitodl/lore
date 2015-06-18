"""
Index information for Haystack.

http://django-haystack.readthedocs.org/en/latest/tutorial.html
"""

from haystack import indexes

from learningresources.models import LearningResource


class LearningResourceIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Index configuration for the LearningResource model.
    """
    text = indexes.CharField(
        document=True, model_attr="content_xml", use_template=True)
    resource_type = indexes.CharField(
        model_attr="learning_resource_type",
        faceted=True,
    )
    course = indexes.CharField(model_attr="course", faceted=True)
    run = indexes.CharField(model_attr="course", faceted=True)

    def get_model(self):
        """Return the model for which this configures indexing."""
        return LearningResource

    def index_queryset(self, using=None):
        """Records to check when updating entire index."""
        return self.get_model().objects.all()

    def prepare_run(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "run" index."""
        return obj.course.run

    def prepare_course(self, obj):  # pylint: disable=no-self-use
        """Define what goes into the "course" index."""
        return obj.course.course_number
