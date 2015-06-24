"""
Search form.
"""
from haystack.forms import FacetedSearchForm


class SearchForm(FacetedSearchForm):
    """Customized version of haystack.forms.FacetedSearchForm"""

    def __init__(self, *args, **kwargs):
        """__init__ override to get repo slug."""
        self.repo_slug = kwargs.pop("repo_slug")
        super(SearchForm, self).__init__(*args, **kwargs)

    def search(self):
        """Override search to filter on repository."""
        sqs = super(SearchForm, self).search()
        return sqs.narrow("repository_exact:{0}".format(self.repo_slug))

    def no_query_found(self):
        """We want to return everything, not nothing (the default)."""
        return self.searchqueryset.narrow(
            "repository_exact:{0}".format(self.repo_slug))
