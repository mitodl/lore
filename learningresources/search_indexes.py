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
    resource_type = indexes.CharField(model_attr="learning_resource_type")

    def get_model(self):
        """Return the model for which this configures indexing."""
        return LearningResource

    def index_queryset(self, using=None):
        """Records to check when updating entire index."""
        return self.get_model().objects.all()
