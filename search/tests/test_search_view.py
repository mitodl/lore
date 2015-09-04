# -*- coding: utf-8 -*-
"""Tests for repostitory listing view search."""
from __future__ import unicode_literals

import logging

from django.core.urlresolvers import reverse

from learningresources.api import create_repo
from search.tests.base import SearchTestCase

log = logging.getLogger(__name__)


class TestSearchView(SearchTestCase):
    """Test Repository listing view.."""

    def test_single_repo(self):
        """
        Search should only return records for one repository
        at a time.
        """
        resp = self.client.get(reverse("repositories", args=(self.repo.slug,)))
        self.assertContains(resp, self.resource.title)

        # Make a new repo with no content.
        new_repo = create_repo("other", "whatever", self.user.id)
        resp = self.client.get(reverse("repositories", args=(new_repo.slug,)))
        self.assertNotContains(resp, self.resource.title)

    def test_terms_with_spaces(self):
        """
        Terms with spaces should show up in facet list correctly.
        """
        for term in self.terms:
            self.resource.terms.add(term)
        resp = self.client.get(reverse("repositories", args=(self.repo.slug,)))
        self.assertContains(resp, "easy")
        self.assertContains(resp, "anc\\u00f2ra")
        self.assertContains(resp, "very difficult")

    def test_db_hits(self):
        """
        Search should not load LearningResources from the database.
        """
        with self.assertNumQueries(10):
            resp = self.client.get(
                reverse("repositories", args=(self.repo.slug,)))

        # We shouldn't have hit the db to get this.
        self.assertContains(resp, self.resource.title)
