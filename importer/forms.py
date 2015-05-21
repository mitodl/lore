"""
Forms for importer.
"""

import os
from tempfile import mkstemp

from django.forms import Form, FileField, ChoiceField

from learningresources.models import Repository
from importer.api import import_course_from_file


class UploadForm(Form):
    """
    Form for allowing a user to upload a video.
    """
    course_file = FileField()
    repository = ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        """
        Fill in choice fields.
        """
        repos = Repository.objects.all().values_list('id', 'name')
        super(UploadForm, self).__init__(*args, **kwargs)

        options = (('', '-- SELECT --'),) + tuple(repos)
        self.fields['repository'].options = options

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

        import_course_from_file(filename, user.id)
