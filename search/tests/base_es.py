# -*- coding: utf-8 -*-
"""
Tests for search engine indexing.

Note that this file started out as a copy
of search/tests/base.py, and was modified to use
the Elasticsearch and Elasticsearch-DSL libraries instead of Haystack.
"""
from __future__ import unicode_literals

import logging

from learningresources.tests.base import LoreTestCase
from search.utils import search_index
from search.sorting import LoreSortingFields
from taxonomy.models import Term, Vocabulary, make_vocab_key

log = logging.getLogger(__name__)


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
            for label in ("easy", "medium", "very difficult", "ancòra", "very")
        ]

    def search(self, query, sorting=LoreSortingFields.DEFAULT_SORTING_FIELD):
        """
        Helper function to perform a search
        """
        return search_index(query, repo_slug=self.repo.slug, sort_by=sorting)

    def count_results(self, query=None):
        """Return count of matching indexed records."""
        return self.search(query).count()

    def count_faceted_results(self, vocab_id, term_id):
        """Return count of matching indexed records by facet."""
        return search_index(
            repo_slug=self.repo.slug,
            terms={make_vocab_key(vocab_id): term_id}
        ).count()
