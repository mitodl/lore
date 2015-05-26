"""
Forms for LearningResources
"""

from __future__ import unicode_literals

from django.forms import ModelForm

from .models import Course


class CourseForm(ModelForm):
    """
    Form for the Course object.
    """
    # pylint: disable=no-init,missing-docstring
    # pylint: disable=old-style-class,too-few-public-methods
    class Meta:
        model = Course
        fields = (
            "repository", "org", "course_number", "semester", "imported_by"
        )
