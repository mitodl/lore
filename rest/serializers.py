"""
REST serializers for taxonomy models
"""

from __future__ import unicode_literals

from rest_framework.serializers import (
    ModelSerializer,
    HiddenField,
    CurrentUserDefault,
    CreateOnlyDefault,
)
from rest_framework.generics import get_object_or_404

from taxonomy.models import Vocabulary, Term
from learningresources.models import Repository
from .util import LambdaDefault, RequiredBooleanField


class RepositorySerializer(ModelSerializer):
    """Serializer for Repository"""

    created_by = HiddenField(
        default=CreateOnlyDefault(CurrentUserDefault())
    )

    class Meta:
        # pylint: disable=missing-docstring
        model = Repository
        fields = (
            'id',
            'slug',
            'name',
            'description',
            'date_created',
            'created_by',
        )
        read_only_fields = (
            'id',
            'slug',
            'date_created',
        )


class VocabularySerializer(ModelSerializer):
    """Serializer for Vocabulary"""

    repository = HiddenField(default=LambdaDefault(
        lambda context: get_object_or_404(
            Repository, slug=context['view'].kwargs['repo_slug']
        )
    ))

    # django-rest-framework mistakenly assumes required=False
    # unless we override the behavior
    required = RequiredBooleanField()

    class Meta:
        # pylint: disable=missing-docstring
        model = Vocabulary
        fields = (
            'id',
            'slug',
            'name',
            'description',
            'vocabulary_type',
            'required',
            'weight',
            'repository',
        )
        read_only_fields = (
            'id',
            'slug',
        )


class TermSerializer(ModelSerializer):
    """Serializer for Term"""

    vocabulary = HiddenField(default=LambdaDefault(
        lambda context: get_object_or_404(
            Vocabulary, slug=context['view'].kwargs['vocab_slug']
        )
    ))

    class Meta:
        # pylint: disable=missing-docstring
        model = Term
        fields = (
            'id',
            'slug',
            'label',
            'weight',
            'vocabulary',
        )
        read_only_fields = (
            'id',
            'slug',
        )
