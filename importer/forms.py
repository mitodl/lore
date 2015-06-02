"""
Forms for importer.
"""

from __future__ import unicode_literals

import os
from tempfile import mkstemp
import logging

from django.forms import Form, FileField, ValidationError

from importer.api import import_course_from_file

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

        log.debug("UploadForm cleaned_data: %s", self.cleaned_data)
        import_course_from_file(
            filename, repo_id, user_id
        )
