"""
A subclass of the Django TestCase which handles
often-needed features, like creating an authenticated
test client.
"""

from django.test import Client
from django.test.testcases import TestCase
from django.contrib.auth.models import User


class LoreTestCase(TestCase):
    """Handle often-needed things in tests."""

    def setUp(self):
        """set up"""
        super(LoreTestCase, self).setUp()
        self.username = 'test'
        self.password = 'test'
        self.user, _ = User.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
