"""
Taxonomy forms
"""
from __future__ import unicode_literals

from django.forms import (
    ModelForm,
    TextInput,
    CheckboxSelectMultiple,
    RadioSelect,
)

from .models import Vocabulary


class VocabularyForm(ModelForm):
    """
    Form for the Vocabulary object.
    """

    # pylint: disable=missing-docstring,no-init
    # pylint: disable=too-few-public-methods
    class Meta:
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
