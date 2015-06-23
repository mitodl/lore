"""
Tests for REST authorization
"""

from __future__ import unicode_literals

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from django.contrib.auth.models import User, Permission

from .base import RESTTestCase
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes


class TestRestAuthorization(RESTTestCase):
    """
    Tests for REST authorization
    """

    def setUp(self):
        super(TestRestAuthorization, self).setUp()

        # add_repo_user is another user with add_repo permission but who
        # does not have access to self.repo
        self.add_repo_user = User.objects.create_user(
            username="creator_user", password=self.PASSWORD
        )
        add_repo_perm = Permission.objects.get(codename=self.ADD_REPO_PERM)
        self.add_repo_user.user_permissions.add(add_repo_perm)

        # curator_user doesn't have add_repo but have view_repo permission on
        # self.repo
        self.curator_user = User.objects.create_user(
            username="curator_user", password=self.PASSWORD
        )
        assign_user_to_repo_group(
            self.curator_user, self.repo, GroupTypes.REPO_CURATOR)

        # author_user doesn't have manage_taxonomy permission
        self.author_user = User.objects.create_user(
            username="author_user", password=self.PASSWORD
        )
        assign_user_to_repo_group(
            self.author_user, self.repo, GroupTypes.REPO_AUTHOR
        )

    def test_repository_create(self):
        """Test create repository authorization"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        # add_repo_user creates a repository
        new_repo_slug = self.create_repository()['slug']

        self.get_repository(new_repo_slug)
        self.get_repository(self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        repos = self.get_repositories()
        self.assertEqual(1, repos['count'])

        # duplicate repository, now that we assigned another repo
        # with same name to user
        self.create_repository(expected_status=HTTP_400_BAD_REQUEST)

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)

        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)

        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

    def test_repository_patch_put(self):
        """Test updating repository"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        input_dict = {
            'name': self.repo.name,
            'description': 'new description'
        }
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_405_METHOD_NOT_ALLOWED)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_repository_delete(self):
        """Test deleting repository"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

        self.logout()
        self.login(self.curator_user.username)

        # curator does have view_repo but nobody is allowed
        # to delete repositories
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_repository_get(self):
        """Test list and view repository"""

        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        # add_repo_user shouldn't be able to see any repositories yet
        self.get_repository(self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        repos = self.get_repositories()
        self.assertEqual(0, repos['count'])

        # add_repo_user creates a repository
        new_repo_slug = self.create_repository()['slug']

        self.get_repository(new_repo_slug)
        repos = self.get_repositories()
        self.assertEqual(1, repos['count'])

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)

        self.assertEqual(1, self.get_repositories()['count'])
        self.get_repository(new_repo_slug,
                            expected_status=HTTP_403_FORBIDDEN)
        self.get_repository(self.repo.slug)

        # switch to user_norepo
        self.logout()
        self.login(self.user_norepo.username)

        self.assertEqual(0, self.get_repositories()['count'])
        self.get_repository(self.repo.slug,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_repositories(expected_status=HTTP_403_FORBIDDEN)
        self.get_repository(self.repo.slug,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_create(self):
        """Test create vocabulary"""
        self.logout()
        self.login(self.curator_user.username)

        self.create_vocabulary(self.repo.slug)
        self.assertEqual(1, self.get_vocabularies(self.repo.slug)['count'])

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        vocab_dict = dict(self.DEFAULT_VOCAB_DICT)
        vocab_dict['name'] = 'other_name'  # prevent name collision

        # author does not have create access, but we haven't disabled this yet
        self.create_vocabulary(
            self.repo.slug, vocab_dict
        )

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.create_vocabulary(self.repo.slug, vocab_dict,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.create_vocabulary(self.repo.slug, vocab_dict,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_put_patch(self):
        """Test update vocabulary"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        self.logout()
        self.login(self.curator_user.username)

        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT)

        # login as author which doesn't have manage_taxonomy permissions
        # but we haven't implemented manage_taxonomy permissions yet so this
        # will go through
        self.logout()
        self.login(self.author_user.username)

        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_delete(self):
        """Test delete vocabulary"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # login as author which doesn't have manage_taxonomy permissions
        # however we don't check for that yet
        self.logout()
        self.login(self.author_user.username)

        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # curator does have manage_taxonomy permissions but delete still
        # not allowed
        self.logout()
        self.login(self.curator_user.username)
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        self.create_term(self.repo.slug, vocab_slug)

        # curator has view_repo but delete not allowed
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_get(self):
        """Test get vocabulary and vocabularies"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(1, self.get_vocabularies(self.repo.slug)['count'])
        self.get_vocabulary(self.repo.slug, vocab_slug)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_vocabularies(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_vocabulary(self.repo.slug, vocab_slug,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_vocabularies(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_vocabulary(self.repo.slug, vocab_slug,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_term_create(self):
        """Test create term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # curator has manage_taxonomy permission
        self.logout()
        self.login(self.curator_user.username)

        self.create_term(self.repo.slug, vocab_slug)
        self.assertEqual(1, self.get_terms(
            self.repo.slug, vocab_slug)['count'])

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        term_dict = dict(self.DEFAULT_TERM_DICT)
        term_dict['label'] = 'other_name'  # prevent name collision

        # author does not have create access, but this isn't implemented yet
        self.create_term(
            self.repo.slug, vocab_slug, term_dict
        )

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

        # as anonymous
        self.logout()
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

    def test_term_put_patch(self):
        """Test update term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']

        self.logout()
        self.login(self.curator_user.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT)

        # login as author which doesn't have manage_taxonomy permissions
        # but this isn't implemented yet so it will go through
        self.logout()
        self.login(self.author_user.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

    def test_term_delete(self):
        """Test delete term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # curator does have manage_taxonomy permissions
        self.logout()
        self.login(self.curator_user.username)
        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_403_FORBIDDEN)

    def test_term_get(self):
        """Test retrieve term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(1, self.get_terms(
            self.repo.slug, vocab_slug)['count'])
        self.get_term(self.repo.slug, vocab_slug, term_slug)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_terms(self.repo.slug, vocab_slug,
                       expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab_slug, term_slug,
                      expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.get_terms(self.repo.slug, vocab_slug,
                       expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab_slug, term_slug,
                      expected_status=HTTP_403_FORBIDDEN)
