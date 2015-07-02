"""
Tests for REST authorization
"""

from __future__ import unicode_literals

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from django.contrib.auth.models import User, Permission

from .base import RESTTestCase
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes, BaseGroupTypes


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

        # author does not have create access
        self.create_vocabulary(
            self.repo.slug, vocab_dict,
            expected_status=HTTP_403_FORBIDDEN
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
        self.logout()
        self.login(self.author_user.username)

        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

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
        self.logout()
        self.login(self.author_user.username)

        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # curator does have manage_taxonomy permissions
        self.logout()
        self.login(self.curator_user.username)
        self.delete_vocabulary(self.repo.slug, vocab_slug)

        # vocab is missing
        self.create_term(self.repo.slug, vocab_slug,
                         expected_status=HTTP_404_NOT_FOUND)
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_404_NOT_FOUND)

        # recreate vocab so we can delete it
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # author has view_repo but delete not allowed
        self.logout()
        self.login(self.author_user.username)
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

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

        # author does not have create access
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
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
        self.logout()
        self.login(self.author_user.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

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
                         expected_status=HTTP_403_FORBIDDEN)

        # curator does have manage_taxonomy permissions
        self.logout()
        self.login(self.curator_user.username)
        self.delete_term(self.repo.slug, vocab_slug, term_slug)

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

    def test_members_get(self):
        """
        Tests for members.
        Get requests: an user can see members if has at least basic permissions
        """
        # add an user to all groups
        for group_type in [GroupTypes.REPO_ADMINISTRATOR,
                           GroupTypes.REPO_CURATOR, GroupTypes.REPO_AUTHOR]:
            assign_user_to_repo_group(
                self.user, self.repo, group_type)

        self.logout()
        # as anonymous
        self.get_members(urlfor='base', repo_slug=self.repo.slug,
                         expected_status=HTTP_403_FORBIDDEN)
        # list of all groups for an user
        self.get_members(urlfor='users', repo_slug=self.repo.slug,
                         username=self.user.username,
                         expected_status=HTTP_403_FORBIDDEN)
        for group_type in BaseGroupTypes.all_base_groups():
            # specific group for an user
            self.get_members(urlfor='users', repo_slug=self.repo.slug,
                             username=self.user.username,
                             group_type=group_type,
                             expected_status=HTTP_403_FORBIDDEN)
            # list of all users for a group
            self.get_members(urlfor='groups', repo_slug=self.repo.slug,
                             group_type=group_type,
                             expected_status=HTTP_403_FORBIDDEN)
            # specific user for a group
            self.get_members(urlfor='groups', repo_slug=self.repo.slug,
                             username=self.user.username,
                             group_type=group_type,
                             expected_status=HTTP_403_FORBIDDEN)

        # any kind of user in the repo groups can retrieve infos
        for user in [self.author_user.username, self.curator_user.username,
                     self.user.username]:
            self.logout()
            self.login(user)
            # list of all groups for an user
            self.get_members(urlfor='base', repo_slug=self.repo.slug)
            # specific group for an user
            self.get_members(urlfor='users', repo_slug=self.repo.slug,
                             username=self.user.username)
            for group_type in BaseGroupTypes.all_base_groups():
                self.get_members(urlfor='users', repo_slug=self.repo.slug,
                                 username=self.user.username,
                                 group_type=group_type)
                # list of all users for a group
                self.get_members(urlfor='groups', repo_slug=self.repo.slug,
                                 group_type=group_type)
                # specific user for a group
                self.get_members(urlfor='groups', repo_slug=self.repo.slug,
                                 username=self.user.username,
                                 group_type=group_type)

    def test_members_create(self):
        """
        Tests for members.
        Post requests: an user can create members only if s/he is admin
        The only URLS where users can be assigned to group or vice versa are
        /api/v1/repositories/<repo>/members/groups/<group_type>/users/
        /api/v1/repositories/<repo>/members/users/<username>/groups/
        """
        self.logout()
        mem_dict_user = {'group_type': 'administrators'}
        mem_dict_groups = {'username': self.user_norepo.username}
        # as anonymous
        self.create_member(urlfor='users', repo_slug=self.repo.slug,
                           mem_dict=mem_dict_user, username=self.user.username,
                           expected_status=HTTP_403_FORBIDDEN)
        for group_type in BaseGroupTypes.all_base_groups():
            self.create_member(urlfor='groups', repo_slug=self.repo.slug,
                               mem_dict=mem_dict_groups,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
        # as author
        self.login(self.author_user.username)
        self.create_member(urlfor='users', repo_slug=self.repo.slug,
                           mem_dict=mem_dict_user, username=self.user.username,
                           expected_status=HTTP_403_FORBIDDEN)
        for group_type in BaseGroupTypes.all_base_groups():
            self.create_member(urlfor='groups', repo_slug=self.repo.slug,
                               mem_dict=mem_dict_groups,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
        # as curator
        self.logout()
        self.login(self.curator_user.username)
        self.create_member(urlfor='users', repo_slug=self.repo.slug,
                           mem_dict=mem_dict_user, username=self.user.username,
                           expected_status=HTTP_403_FORBIDDEN)
        for group_type in BaseGroupTypes.all_base_groups():
            self.create_member(urlfor='groups', repo_slug=self.repo.slug,
                               mem_dict=mem_dict_groups,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
        # as administrator
        self.logout()
        self.login(self.user.username)
        self.create_member(urlfor='users', repo_slug=self.repo.slug,
                           mem_dict=mem_dict_user, username=self.user.username)
        for group_type in BaseGroupTypes.all_base_groups():
            self.create_member(urlfor='groups', repo_slug=self.repo.slug,
                               mem_dict=mem_dict_groups,
                               group_type=group_type)

    def test_members_delete(self):
        """
        Tests for members.
        Delete requests: an user can delete members only if s/he is admin
        The only URLS where users can be deleted from a group or vice versa are
        /api/v1/repositories/<repo>/members/groups/<group_type>/users/<username>
        /api/v1/repositories/<repo>/members/users/<username>/groups/<group_type>
        """
        for group_type in BaseGroupTypes.all_base_groups():
            # as anonymous
            self.logout()
            self.delete_member(urlfor='users', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
            self.delete_member(urlfor='groups', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
            # as author
            self.login(self.author_user.username)
            self.delete_member(urlfor='users', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
            self.delete_member(urlfor='groups', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
            # as curator
            self.logout()
            self.login(self.curator_user.username)
            self.delete_member(urlfor='users', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
            self.delete_member(urlfor='groups', repo_slug=self.repo.slug,
                               username=self.user.username,
                               group_type=group_type,
                               expected_status=HTTP_403_FORBIDDEN)
        # different loop because the actual deletion can impact the other tests
        for group_type in BaseGroupTypes.all_base_groups():
            # as administrator
            # deleting a different username because deleting self from admin is
            # a special case (handled in different tests)
            self.logout()
            self.login(self.user.username)
            self.delete_member(urlfor='users', repo_slug=self.repo.slug,
                               username=self.author_user.username,
                               group_type=group_type)
            self.delete_member(urlfor='groups', repo_slug=self.repo.slug,
                               username=self.author_user.username,
                               group_type=group_type)
