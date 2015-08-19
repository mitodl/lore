"""
Search form.
"""
from __future__ import unicode_literals

from haystack.forms import FacetedSearchForm
from search.sorting import LoreSortingFields


class SearchForm(FacetedSearchForm):
    """Customized version of haystack.forms.FacetedSearchForm"""

    def __init__(self, *args, **kwargs):
        """__init__ override to get repo slug and sorting."""
        self.repo_slug = kwargs.pop("repo_slug")
        self.sortby = kwargs.pop("sortby")
        super(SearchForm, self).__init__(*args, **kwargs)

    def search(self):
        """Override search to filter on repository."""
        sqs = super(SearchForm, self).search()
        sqs = sqs.narrow("repository_exact:{0}".format(self.repo_slug))
        return sqs.order_by('-{0}'.format(self.sortby)).order_by(
            LoreSortingFields.BASE_SORTING_FIELD)

    def no_query_found(self):
        """We want to return everything, not nothing (the default)."""
        sqs = self.searchqueryset.narrow(
            "repository_exact:{0}".format(self.repo_slug))
        return sqs.order_by('-{0}'.format(self.sortby)).order_by(
            LoreSortingFields.BASE_SORTING_FIELD)
