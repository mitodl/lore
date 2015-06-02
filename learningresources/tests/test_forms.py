"""
Tests for learningresources forms.
"""
from __future__ import unicode_literals

from learningresources.forms import CourseForm
from learningresources.models import Repository, Course

from .base import LoreTestCase


class TestCourseForm(LoreTestCase):
    """Test the Course form."""

    def setUp(self):
        """Initialize"""
        super(TestCourseForm, self).setUp()
        self.repo, _ = Repository.objects.get_or_create(
            name="tester repo", created_by_id=self.user.id,
            slug="tester-repo")

    def test_init(self):
        """Get the form page."""
        data = {
            "imported_by": self.user.id,
            "repository": self.repo.id,
            "org": "fake org", "run": "Febtober",
            "course_number": "1234",
        }
        form = CourseForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(Course.objects.count() == 0)
        form.save(self.user)
        self.assertTrue(Course.objects.count() == 1)
