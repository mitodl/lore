"""
Search form.
"""

from haystack.forms import FacetedSearchForm


class SearchForm(FacetedSearchForm):
    """Customized version of haystack.forms.FacetedSearchForm"""
    def no_query_found(self):
        """We want to return everything, not nothing (the default)."""
        return self.searchqueryset.all()
