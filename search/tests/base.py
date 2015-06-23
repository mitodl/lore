"""Tests for search engine indexing."""

from learningresources.tests.base import LoreTestCase
from search.forms import SearchForm
from taxonomy.models import Term, Vocabulary


class SearchTestCase(LoreTestCase):
    """Test Elasticsearch indexing."""

    def setUp(self):
        """Create a vocabulary for our tests."""
        super(SearchTestCase, self).setUp()
        self.vocabulary = Vocabulary.objects.create(
            repository_id=self.repo.id, name="difficulty",
            description="difficulty", required=False, vocabulary_type="f",
            weight=1
        )
        self.terms = [
            Term.objects.create(
                vocabulary_id=self.vocabulary.id, label=label, weight=1
            )
            for label in ("easy", "medium", "difficult")
        ]

    def count_results(self, query):
        """Return count of matching indexed records."""
        form = SearchForm(data={"q": query}, repo_slug=self.repo.slug)
        return form.search().count()

    def count_faceted_results(self, vocab, term):
        """Return count of matching indexed records by facet."""
        facet_query = "{0}_exact:{1}".format(vocab, term)
        form = SearchForm(
            selected_facets=[facet_query], repo_slug=self.repo.slug)
        return form.search().count()
