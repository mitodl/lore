"""
Test the importer views to make sure they work.
"""

from __future__ import unicode_literals

from django.test import Client
from django.test.testcases import TestCase
from django.contrib.auth.models import User

from learningresources.models import Repository

HTTP_OK = 200


class TestViews(TestCase):
    """Hit each view."""

    def setUp(self):
        """initialize"""
        super(TestViews, self).setUp()
        self.username = 'test'
        self.password = 'test'
        user = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()

    def test_welcome(self):
        """Welcome page."""
        client = Client()
        resp = client.get("/welcome", follow=True)
        self.assertTrue(resp.status_code == HTTP_OK)
        body = resp.content.decode("utf-8")
        self.assertTrue("<h1>Welcome</h1>" in body)

    def test_create_repo_get(self):
        """GET repo creation page."""
        client = Client()
        client.login(username=self.username, password=self.password)
        resp = client.get("/create_repo", follow=True)
        body = resp.content.decode("utf-8")
        self.assertTrue('<h1>Create repository</h1>' in body)

    def test_upload_post(self):
        """POST upload page."""
        client = Client()
        client.login(username=self.username, password=self.password)
        self.assertTrue(Repository.objects.count() == 0)
        client.post(
            "/create_repo/",
            {"name": "test name", "description": "test description"},
            follow=True
        )
        self.assertTrue(Repository.objects.count() == 1)
