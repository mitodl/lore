"""
Taxonomy forms
"""

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

    # disable: warning=missing-docstring,old-style-class,no-init,
    # disable: warning=too-few-public-methods
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
