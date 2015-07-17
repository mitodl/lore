# -*- coding: utf-8 -*-
"""Tests for repostitory listing view search."""

from django.core.urlresolvers import reverse

from learningresources.api import create_repo
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes
from search.tests.base import SearchTestCase


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
        assign_user_to_repo_group(
            self.user,
            new_repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
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
        self.assertContains(resp, "ancòra")
        self.assertContains(resp, "very difficult")
