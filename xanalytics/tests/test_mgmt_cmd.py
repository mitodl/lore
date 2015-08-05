"""
Test the xanalytics management command(s).
"""

import logging

from django.core.management import call_command
from django.core.management.base import CommandError

from learningresources.models import LearningResource
from learningresources.tests.base import LoreTestCase

log = logging.getLogger(__name__)


class TestMgmtCmd(LoreTestCase):
    """
    Test management commands.
    """

    def test_update(self):
        """Test kicking off a request."""
        res = LearningResource.objects.get(id=self.resource.id)
        self.assertTrue(
            all([
                x == 0 for x in
                (res.xa_nr_views, res.xa_nr_attempts, res.xa_avg_grade)
            ])
        )

        # Calling command should populate the xanalytics fields.
        call_command("populate_xanalytics", "{0}".format(self.course.id))

        # Pull fresh from db.
        res = LearningResource.objects.get(id=self.resource.id)
        self.assertTrue(
            all([
                x > 0 for x in
                (res.xa_nr_views, res.xa_nr_attempts, res.xa_avg_grade)
            ])
        )

    def test_arg(self):
        """Must pass a course ID."""
        with self.assertRaises(CommandError):
            call_command("populate_xanalytics")

        # Runs, no errors.
        self.assertTrue(
            call_command(
                "populate_xanalytics", "{0}".format(self.course.id)) is None
        )

        # Course ID must exist in the database.
        max_id = LearningResource.objects.all().order_by('-id').first().id
        with self.assertRaises(CommandError):
            call_command("populate_xanalytics", "{0}".format(max_id+1))
