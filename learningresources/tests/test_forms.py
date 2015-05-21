"""
Tests for learningresources forms.
"""
from __future__ import unicode_literals

from django.test.testcases import TestCase
from django.contrib.auth.models import User

from learningresources.forms import CourseForm
from learningresources.models import Repository, Course


class TestCourseForm(TestCase):
    """Test the Course form."""

    def setUp(self):
        """Initialize"""
        self.user, _ = User.objects.get_or_create(username="tester dude")
        self.repo, _ = Repository.objects.get_or_create(
            name="tester repo", created_by_id=self.user.id)

    def test_init(self):
        """Get the form page."""
        data = {
            "imported_by": self.user.id,
            "repository": self.repo.id,
            "org": "fake org", "semester": "Febtober",
            "course_number": "1234",
        }
        form = CourseForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(Course.objects.count() == 0)
        form.save(self.user)
        self.assertTrue(Course.objects.count() == 1)
