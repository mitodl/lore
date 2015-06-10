"""
A subclass of the Django TestCase which handles
often-needed features, like creating an authenticated
test client.
"""

from django.test import Client
from django.test.testcases import TestCase
from django.contrib.auth.models import User, Permission

from learningresources.models import Repository
from learningresources.api import create_repo
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes


class LoreTestCase(TestCase):
    """Handle often-needed things in tests."""
    USERNAME = 'test'
    PASSWORD = 'test'
    USERNAME_NO_REPO = 'test2'

    ADD_REPO_PERM = 'add_{}'.format(
        Repository._meta.model_name  # pylint: disable=protected-access
    )

    def login(self, username):
        """assumes the password is the same"""
        self.client.login(
            username=username,
            password=self.PASSWORD
        )

    def logout(self):
        """just a client logout"""
        self.client.logout()

    def setUp(self):
        """set up"""
        super(LoreTestCase, self).setUp()
        self.user = User.objects.create_user(
            username=self.USERNAME, password=self.PASSWORD
        )
        add_repo_perm = Permission.objects.get(codename=self.ADD_REPO_PERM)
        self.user.user_permissions.add(add_repo_perm)
        # user without permission to add a repo
        self.user_norepo = User.objects.create_user(
            username=self.USERNAME_NO_REPO, password=self.PASSWORD
        )

        self.repo = create_repo(
            name="test repo",
            description="just a test",
            user_id=self.user.id,
        )

        assign_user_to_repo_group(self.user,
                                  self.repo,
                                  GroupTypes.repo_administrator)

        self.client = Client()
        self.login(username=self.USERNAME)
