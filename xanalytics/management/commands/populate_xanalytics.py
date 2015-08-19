"""Management command to populate xanalytics data by course ID."""

import logging
from random import randint

from django.core.management.base import BaseCommand, CommandError

from learningresources.models import Course

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Populate xanalytics data for a course."""

    help = "Populate xanalytics data for a course by primary key."

    def add_arguments(self, parser):
        """Add argparse arguments."""
        parser.add_argument('course_id', nargs=1, type=int)

    def handle(self, *args, **options):
        """Run the command."""
        try:
            # Args are passed in a list; there's only one, so
            # we take [0] of the list.
            course_id = options["course_id"][0]
        except (KeyError, TypeError, IndexError):
            raise CommandError("course ID is required")

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise CommandError("invalid course ID")

        # This should call importer.tasks.populate_xanalytics_fields
        # once the xanalytics API is ready.
        for resource in course.resources.all().iterator():
            resource.xa_nr_views = randint(1, 10000)
            resource.xa_nr_attempts = randint(1, 1000)
            resource.xa_avg_grade = randint(65, 101)
            resource.save()
