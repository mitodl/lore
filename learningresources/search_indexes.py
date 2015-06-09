"""
Index information for Haystack.

http://django-haystack.readthedocs.org/en/latest/tutorial.html
"""
from haystack.indexes import (
    SearchIndex, Indexable, CharField
)  # pragma: no cover

from learningresources.models import LearningResource  # pragma: no cover


class LearningResourceIndex(SearchIndex, Indexable):  # pragma: no cover
    """
    Index configuration for the LearningResource model.
    """
    text = CharField(
        document=True, model_attr="content_xml", use_template=True)

    def get_model(self):
        """Return the model for which this configures indexing."""
        return LearningResource

    def index_queryset(self, using=None):
        """Records to check when updating entire index."""
        return self.get_model().objects.all()
