"""
Controllers for REST app
"""

from __future__ import unicode_literals

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated

from roles.permissions import GroupTypes
from roles.api import assign_user_to_repo_group
from rest.serializers import (
    VocabularySerializer,
    RepositorySerializer,
    TermSerializer,
)
from rest.permissions import (
    AddRepoPermission,
    ViewRepoPermission,
    ViewVocabularyPermission,
    ViewTermPermission,
    ManageTaxonomyPermission,
)
from learningresources.models import Repository
from learningresources.api import (
    get_repos,
)


# pylint: disable=too-many-ancestors
class RepositoryList(ListCreateAPIView):
    """REST list view for Repository"""
    serializer_class = RepositorySerializer
    permission_classes = (
        AddRepoPermission,
        IsAuthenticated,
    )

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('repository-detail', kwargs={'repo_slug': data['slug']})
        return {'Location': url}

    def get_queryset(self):
        """Filter to these repositories"""

        repo_ids = [repo.id for repo in get_repos(self.request.user.id)]
        return Repository.objects.filter(id__in=repo_ids).order_by('id')

    def perform_create(self, serializer):
        """Create a new repository"""
        # pylint: disable=protected-access
        repo = serializer.save()
        assign_user_to_repo_group(
            self.request.user,
            repo,
            GroupTypes.REPO_ADMINISTRATOR
        )


class RepositoryDetail(RetrieveAPIView):
    """REST detail view for Repository"""
    serializer_class = RepositorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'repo_slug'
    permission_classes = (
        ViewRepoPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to this repository"""
        return Repository.objects.filter(slug=self.kwargs['repo_slug'])


class VocabularyList(ListCreateAPIView):
    """REST list view for Vocabulary"""
    serializer_class = VocabularySerializer
    permission_classes = (
        ViewRepoPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to vocabularies for a repository"""
        return Repository.objects.get(
            slug=self.kwargs['repo_slug']).vocabulary_set.order_by('id')

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('vocabulary-detail', kwargs={
            'repo_slug': self.kwargs['repo_slug'],
            'vocab_slug': data['slug'],
        })
        return {'Location': url}


class VocabularyDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Vocabulary"""
    serializer_class = VocabularySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'vocab_slug'
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a vocabulary within a repository"""
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        return repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )


class TermList(ListCreateAPIView):
    """REST list view for Term"""
    serializer_class = TermSerializer
    permission_classes = (
        ViewVocabularyPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to terms within a vocabulary and repository"""

        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        vocabs = repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )
        if not vocabs.exists():
            return []

        return vocabs.first().term_set.order_by('id')

    def get_success_headers(self, data):
        """Add Location header for model create"""
        url = reverse('term-detail', kwargs={
            'vocab_slug': self.kwargs['vocab_slug'],
            'repo_slug': self.kwargs['repo_slug'],
            'term_slug': data['slug'],
        })
        return {'Location': url}


class TermDetail(RetrieveUpdateDestroyAPIView):
    """REST detail view for Term"""
    serializer_class = TermSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'term_slug'
    permission_classes = (
        ViewTermPermission,
        ManageTaxonomyPermission,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Filter to a term within a vocabulary within a repository"""
        repo = Repository.objects.get(slug=self.kwargs['repo_slug'])
        vocabs = repo.vocabulary_set.filter(
            slug=self.kwargs['vocab_slug']
        )
        if not vocabs.exists():
            return []

        return vocabs.first().term_set.filter(
            slug=self.kwargs['term_slug']
        )
