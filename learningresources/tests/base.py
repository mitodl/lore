"""
A subclass of the Django TestCase which handles
often-needed features, like creating an authenticated
test client.
"""

from django.test import Client
from django.test.testcases import TestCase
from django.contrib.auth.models import User

from learningresources.api import create_repo


class LoreTestCase(TestCase):
    """Handle often-needed things in tests."""
    USERNAME = 'test'
    PASSWORD = 'test'

    def setUp(self):
        """set up"""
        super(LoreTestCase, self).setUp()
        self.user = User.objects.create_user(
            username=self.USERNAME, password=self.PASSWORD
        )
        self.client = Client()
        self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD
        )

        self.repo = create_repo(
            name="test repo",
            description="just a test",
            user_id=self.user.id,
        )
