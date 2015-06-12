"""
Search form.
"""

from haystack.forms import SearchForm as HaystackSearchForm


class SearchForm(HaystackSearchForm):
    """Customized version of haystack.forms.SearchForm"""
    def no_query_found(self):
        """We want to return everything, not nothing (the default)."""
        return self.searchqueryset.all()
