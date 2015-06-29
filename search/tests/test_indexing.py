"""Tests for search engine indexing."""

from search.tests.base import SearchTestCase


class TestIndexing(SearchTestCase):
    """Test Elasticsearch indexing."""

    def test_index_on_save(self):
        """Index a LearningObject upon creation."""
        search_text = "The quick brown fox."
        self.assertTrue(self.count_results(search_text) == 0)
        self.resource.content_xml = search_text
        self.resource.save()
        self.assertTrue(self.count_results(search_text) == 1)

    def test_index_vocabulary(self):
        """
        Test that LearningResource indexes are updated when a
        a term is added or removed.
        """
        term = self.terms[0]
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 0)
        self.resource.terms.add(term)
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 1)
        self.resource.terms.remove(term)
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 0)

    def test_strip_xml(self):
        """Indexed content_xml should have XML stripped."""
        xml = "<tag>you're it</tag>"
        self.resource.content_xml = xml
        self.resource.save()
        self.assertTrue(self.count_results("you're it") == 1)
        self.assertTrue(self.count_results(xml) == 0)
