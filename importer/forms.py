"""
Forms for importer.
"""

from __future__ import unicode_literals

import os
from tempfile import mkstemp
import logging

from django.forms import Form, FileField, ChoiceField

from learningresources.models import Repository
from importer.api import import_course_from_file

log = logging.getLogger(__name__)


class UploadForm(Form):
    """
    Form for allowing a user to upload a video.
    """
    course_file = FileField()
    repository = ChoiceField()

    def __init__(self, *args, **kwargs):
        """
        Fill in choice fields.
        """
        log.debug("in UploadForm __init__")
        repos = Repository.objects.all().values_list('id', 'name')
        log.debug("repos from db: %s", repos)
        super(UploadForm, self).__init__(*args, **kwargs)

        options = (('', '-- SELECT --'),) + tuple(repos)
        self.fields['repository'].choices = options

    def save(self, user):
        """
        Receives the request.FILES from the view.

        Args:
            user (auth.User): request.user
        """
        # Assumes a single file, because we only accept
        # one at a time.
        uploaded_file = list(self.files.values())[0]
        _, ext = os.path.splitext(uploaded_file.name)

        # Save the uploaded file into a temp file.
        handle, filename = mkstemp(suffix=ext)
        os.close(handle)

        with open(filename, 'wb') as temp:
            for chunk in uploaded_file:
                temp.write(chunk)

        log.debug("UploadForm cleaned_data: %s", self.cleaned_data)
        import_course_from_file(
            filename, self.cleaned_data["repository"], user.id
        )
