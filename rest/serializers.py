"""
REST serializers for taxonomy models
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    HiddenField,
    CurrentUserDefault,
    CreateOnlyDefault,
    CharField,
    ChoiceField,
    ValidationError,
    StringRelatedField,
    SlugRelatedField,
)

from rest.util import LambdaDefault, RequiredBooleanField
from roles.permissions import BaseGroupTypes
from taxonomy.models import Vocabulary, Term
from learningresources.models import (
    Repository,
    LearningResource,
    StaticAsset,
)


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


class GroupSerializer(Serializer):
    """
    Serializer for base_group_type
    """
    group_type = ChoiceField(
        choices=BaseGroupTypes.all_base_groups()
    )

    def validate_group_type(self, value):
        """Validate group_type"""
        # pylint: disable=no-self-use
        if value not in BaseGroupTypes.all_base_groups():  # pragma: no cover
            raise ValidationError(
                'group "{group}" is not valid'.format(group=value)
            )
        return value


class UserSerializer(Serializer):
    """
    Serializer for user
    """
    username = CharField()

    def validate_username(self, value):
        """Validate username"""
        # pylint: disable=no-self-use
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:  # pragma: no cover
            raise ValidationError(
                'user "{user}" is not available'.format(user=value)
            )
        return value


class UserGroupSerializer(UserSerializer, GroupSerializer):
    """
    Serializer for username base_group_type association
    """


class LearningResourceSerializer(ModelSerializer):
    """Serializer for LearningResource"""

    learning_resource_type = StringRelatedField()
    terms = SlugRelatedField(
        many=True, slug_field='slug', queryset=Term.objects.all())

    class Meta:
        # pylint: disable=missing-docstring
        model = LearningResource
        fields = (
            'id',
            'learning_resource_type',
            'static_assets',
            'title',
            'description',
            'content_xml',
            'materialized_path',
            'url_path',
            'parent',
            'copyright',
            'xa_nr_views',
            'xa_nr_attempts',
            'xa_avg_grade',
            'xa_histogram_grade',
            'terms',
        )
        read_only_fields = tuple(set(fields) - {'description'})

    def validate_terms(self, terms):
        """
        Validate that this LearningResource's learning_resource_type
        is supported by the vocabulary of each term being added
        """
        resource_type = self.instance.learning_resource_type
        for term in terms:
            if not term.vocabulary.learning_resource_types.filter(
                    name=resource_type.name).exists():
                raise ValidationError(
                    "Term {} is not supported "
                    "for this learning resource".format(term.label))
        return terms


class StaticAssetSerializer(ModelSerializer):
    """Serializer for StaticAsset"""

    class Meta:
        # pylint: disable=missing-docstring
        model = StaticAsset
        fields = (
            'id',
            'asset',
        )
        read_only_fields = (
            'id',
            'asset',
        )
