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
from django.db import transaction
from django.utils.text import slugify

from .models import Vocabulary


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

    # pylint: disable=arguments-differ
    # commit argument is omitted since we need to update slug
    @transaction.atomic
    def save(self):
        """
        Save the vocabulary form
        """
        vocab = super(VocabularyForm, self).save(commit=False)
        slug = slugify(vocab.name)
        count = 1
        while Vocabulary.objects.filter(slug=slug).exists():
            slug = "{0}{1}".format(slugify(vocab.name), count)
            count += 1
        vocab.slug = slug
        vocab.save()
        self.save_m2m()
