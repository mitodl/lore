"""
Forms for LORE.
"""

from __future__ import unicode_literals

import os
from tempfile import mkstemp
import logging

from django.forms import (
    Form, FileField, ValidationError, ModelForm, TextInput,
    CheckboxSelectMultiple, RadioSelect,
)
from django.db import transaction

from importer.tasks import import_file
from learningresources.models import Course, Repository
from taxonomy.models import Vocabulary

log = logging.getLogger(__name__)


class UploadForm(Form):
    """
    Form for allowing a user to upload a video.
    """
    course_file = FileField()

    def __init__(self, *args, **kwargs):
        """
        Fill in choice fields.
        """
        super(UploadForm, self).__init__(*args, **kwargs)

    def clean_course_file(self):
        """Only certain extensions are allowed."""
        upload = self.cleaned_data["course_file"]
        log.debug("checking filename %s", upload.name)
        for ext in (".zip", ".tar.gz", ".tgz"):
            if upload.name.endswith(ext):
                log.debug("the filename is good")
                upload.ext = ext
                log.debug("setting upload.ext to %s", ext)
                return upload
        log.debug("got to end, so the file is bad")
        raise ValidationError("Unsupported file type.")

    def save(self, user_id, repo_id):
        """
        Receives the request.FILES from the view.

        Args:
            user_id (int): primary key of the user uploading the course.
            repo_id (int): primary key of repository we're uploading to
        """
        # Assumes a single file, because we only accept
        # one at a time.
        uploaded_file = self.cleaned_data["course_file"]

        # Save the uploaded file into a temp file.
        handle, filename = mkstemp(suffix=uploaded_file.ext)
        os.close(handle)

        with open(filename, 'wb') as temp:
            for chunk in uploaded_file:
                temp.write(chunk)

        import_file.delay(filename, repo_id, user_id)


class CourseForm(ModelForm):
    """
    Form for the Course object.
    """
    class Meta:  # pylint: disable=missing-docstring
        model = Course
        fields = (
            "repository", "org", "course_number", "run", "imported_by"
        )


class RepositoryForm(ModelForm):
    """
    Form for the Repository object.
    """
    class Meta:  # pylint: disable=missing-docstring
        model = Repository
        fields = ("name", "description")

    # pylint: disable=signature-differs
    # The ModelForm.save() accepts "commit" and this doesn't, because
    # we always set commit=False then add the user because created_by is
    # not part of the form, and shouldn't be.
    @transaction.atomic
    def save(self, user):
        """
        Save a newly-created form.
        """
        repo = super(RepositoryForm, self).save(commit=False)
        repo.created_by = user
        repo.save()
        return repo


class VocabularyForm(ModelForm):
    """
    Form for the Vocabulary object.
    """

    class Meta:
        # pylint: disable=missing-docstring
        model = Vocabulary

        fields = [
            'name',
            'description',
            'learning_resource_types',
            'vocabulary_type'
        ]
        widgets = {
            'name': TextInput(),
            'learning_resource_types': CheckboxSelectMultiple(),
            'vocabulary_type': RadioSelect(),
        }
