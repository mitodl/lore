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
