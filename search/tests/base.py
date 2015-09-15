# -*- coding: utf-8 -*-
"""Tests for search engine indexing."""
from __future__ import unicode_literals

from learningresources.tests.base import LoreTestCase
from search.api import construct_queryset
from search.sorting import LoreSortingFields
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
            for label in ("easy", "medium", "very difficult", "ancòra")
        ]

    def search(self, query, sorting=LoreSortingFields.DEFAULT_SORTING_FIELD):
        """
        Helper function to perform a search
        """
        return construct_queryset(
            repo_slug=self.repo.slug, query=query, sortby=sorting)

    def count_results(self, query):
        """Return count of matching indexed records."""
        return self.search(query).count()

    def count_faceted_results(self, vocab, term):
        """Return count of matching indexed records by facet."""
        facet_query = "{0}_exact:{1}".format(vocab, term)
        return construct_queryset(
            repo_slug=self.repo.slug,
            selected_facets=[facet_query]
        ).count()
