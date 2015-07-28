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
    FileField,
    SerializerMethodField,
    IntegerField,
)

from rest.util import LambdaDefault, RequiredBooleanField
from roles.permissions import BaseGroupTypes
from taxonomy.models import Vocabulary, Term
from learningresources.models import (
    Repository,
    LearningResource,
    StaticAsset,
    LearningResourceType,
    STATIC_ASSET_BASEPATH
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
    # not technically a slug but the name is unique so we can use it as a key
    learning_resource_types = SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=LearningResourceType.objects.all()
    )
    terms = SerializerMethodField()

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
            'learning_resource_types',
            'terms',
            'multi_terms',
        )
        read_only_fields = (
            'id',
            'slug',
        )

    @staticmethod
    def get_terms(obj):
        """List of terms for vocabulary"""
        return [TermSerializer(term).data for term in obj.term_set.all()]


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


class LearningResourceTypeSerializer(ModelSerializer):
    """Serializer for LearningResourceType"""
    class Meta:
        # pylint: disable=missing-docstring
        model = LearningResourceType
        fields = ('name',)
        read_only_fields = fields


class LearningResourceSerializer(ModelSerializer):
    """Serializer for LearningResource"""

    learning_resource_type = StringRelatedField()
    terms = SlugRelatedField(
        many=True, slug_field='slug', queryset=Term.objects.all())
    preview_url = SerializerMethodField()

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
            'preview_url',
        )
        read_only_fields = tuple(set(fields) - {'description', 'terms'})

    def validate_terms(self, terms):
        """
        Validate that
        1- this LearningResource's learning_resource_type
           is supported by the vocabulary of each term being added
        2- There are no multiple terms belonging to a vocabulary with
           "multi_term" field set to False
        """
        resource_type = self.instance.learning_resource_type
        vocabulary_cache = {}
        for term in terms:
            if not term.vocabulary.learning_resource_types.filter(
                    name=resource_type.name).exists():
                raise ValidationError(
                    "Term {} is not supported "
                    "for this LearningResource".format(term.label))
            if not term.vocabulary.multi_terms:
                vocabulary_cache.setdefault(
                    term.vocabulary.id, []).append(term.id)
                if len(vocabulary_cache[term.vocabulary.id]) > 1:
                    raise ValidationError(
                        "Vocabulary {0} can have only one term "
                        "assigned to the same LearningResource".format(
                            term.vocabulary.name
                        )
                    )
        return terms

    @staticmethod
    def get_preview_url(obj):
        """Construct preview URL for LearningResource."""
        return obj.get_preview_url()


class StaticAssetSerializer(ModelSerializer):
    """Serializer for StaticAsset"""

    asset = FileField(use_url=True)
    name = SerializerMethodField()

    class Meta:
        # pylint: disable=missing-docstring
        model = StaticAsset
        fields = (
            'id',
            'asset',
            'name',
        )
        read_only_fields = (
            'id',
            'asset',
            'name',
        )

    @staticmethod
    def get_name(static_asset_obj):
        """Method to get the name of the asset"""
        basepath = STATIC_ASSET_BASEPATH.format(
            org=static_asset_obj.course.org,
            course_number=static_asset_obj.course.course_number,
            run=static_asset_obj.course.run,
        )
        return static_asset_obj.asset.name.replace(basepath, '')


class LearningResourceExportSerializer(Serializer):
    """Serializer for exporting id for LearningResource."""
    id = IntegerField()
