"""
Unit tests for REST api
"""
from __future__ import unicode_literals

from operator import itemgetter

from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from roles.api import (
    assign_user_to_repo_group,
    remove_user_from_repo_group,
    list_users_in_repo,
)
from roles.permissions import GroupTypes, BaseGroupTypes
from rest.tests.base import (
    RESTTestCase,
    RESTAuthTestCase,
)


class TestMembers(RESTTestCase):
    """
    Specific Class for the members because test need different users
    """
    def setUp(self):
        super(TestMembers, self).setUp()
        # Create some new users.
        self.author_user = User.objects.create_user(
            username="author_user", password=self.PASSWORD
        )
        self.curator_user = User.objects.create_user(
            username="curator_user", password=self.PASSWORD
        )
        self.admin_user = User.objects.create_user(
            username="admin_user", password=self.PASSWORD
        )
        self.admin_user2 = User.objects.create_user(
            username="admin_user2", password=self.PASSWORD
        )
        # List of all user.
        self.all_user_repo = [
            self.author_user,
            self.curator_user,
            self.admin_user
        ]
        self.remove_all_users_from_repo()

        # No user is logged in by default.
        self.logout()

    def remove_all_users_from_repo(self):
        """
        Helper method to remove all users from all repo groups.
        """
        # Remove all the users from all the groups in the repo.
        for user_group in list_users_in_repo(self.repo):
            user = User.objects.get(username=user_group.username)
            group_type = GroupTypes.get_repo_groupname_by_base(
                user_group.group_type
            )
            remove_user_from_repo_group(user, self.repo, group_type)

    def add_users_to_repo(self):
        """
        Helper function to add some users to the repository groups.
        """
        # add only 3 users to 3 different groups
        assign_user_to_repo_group(
            self.author_user, self.repo, GroupTypes.REPO_AUTHOR)
        assign_user_to_repo_group(
            self.curator_user, self.repo, GroupTypes.REPO_CURATOR)
        assign_user_to_repo_group(
            self.admin_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)

    def assert_users_count(self, authors=0, curators=0, admins=0):
        """
        Helper function to count users in the different groups
        """
        total = authors + curators + admins
        self.assertEqual(len(list_users_in_repo(self.repo)), total)
        self.assertEqual(
            len(list_users_in_repo(self.repo, BaseGroupTypes.AUTHORS)),
            authors
        )
        self.assertEqual(
            len(list_users_in_repo(self.repo, BaseGroupTypes.CURATORS)),
            curators
        )
        self.assertEqual(
            len(list_users_in_repo(self.repo, BaseGroupTypes.ADMINISTRATORS)),
            admins
        )

    def test_members_get(self):
        """
        Members GET
        """
        all_members = sorted(
            [
                {'username': 'admin_user', 'group_type': 'administrators'},
                {'username': 'curator_user', 'group_type': 'curators'},
                {'username': 'author_user', 'group_type': 'authors'}
            ],
            key=itemgetter('username')
        )
        author_member = [{'group_type': 'authors'}]
        curator_member = [{'group_type': 'curators'}]
        admin_member = [{'group_type': 'administrators'}]
        author_user_member = [{'username': 'author_user'}]
        curator_user_member = [{'username': 'curator_user'}]
        admin_user_member = [{'username': 'admin_user'}]
        # Populate repo groups.
        self.add_users_to_repo()
        # all kind of users will get the same results
        for repo_user in self.all_user_repo:
            self.login(repo_user.username)
            # get all the users for all the groups
            resp_dict = self.get_members(
                urlfor='base',
                repo_slug=self.repo.slug
            )
            self.assertListEqual(
                sorted(
                    resp_dict['results'],
                    key=itemgetter('username')
                ),
                all_members
            )
            # get all the groups for specific users
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.author_user.username
            )
            self.assertListEqual(resp_dict['results'], author_member)
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.curator_user.username
            )
            self.assertListEqual(resp_dict['results'], curator_member)
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.admin_user.username
            )
            self.assertListEqual(resp_dict['results'], admin_member)
            # get one group for a specific users
            # author
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.AUTHORS
            )
            self.assertEqual(resp_dict, author_member[0])
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.CURATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            # curator
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.AUTHORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.CURATORS
            )
            self.assertEqual(resp_dict, curator_member[0])
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            # administrator
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.AUTHORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.CURATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='users',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS
            )
            self.assertEqual(resp_dict, admin_member[0])
            # get all the users for specific group
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                group_type=BaseGroupTypes.AUTHORS
            )
            self.assertListEqual(resp_dict['results'], author_user_member)
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                group_type=BaseGroupTypes.CURATORS
            )
            self.assertListEqual(resp_dict['results'], curator_user_member)
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                group_type=BaseGroupTypes.ADMINISTRATORS
            )
            self.assertListEqual(resp_dict['results'], admin_user_member)
            # get one user for a specific group
            # author
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.AUTHORS
            )
            self.assertEqual(resp_dict, author_user_member[0])
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.CURATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.author_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            # curator
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.AUTHORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.CURATORS
            )
            self.assertEqual(resp_dict, curator_user_member[0])
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.curator_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            # administrator
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.AUTHORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.CURATORS,
                expected_status=HTTP_404_NOT_FOUND,
                skip_options_head_test=True
            )
            resp_dict = self.get_members(
                urlfor='groups',
                repo_slug=self.repo.slug,
                username=self.admin_user.username,
                group_type=BaseGroupTypes.ADMINISTRATORS
            )
            self.assertEqual(resp_dict, admin_user_member[0])

    def test_members_create(self):
        """
        Members POST
        Testing only using an administrator used logged in.
        All the other kind of users don't have permissions to handle users.
        (tests for other users in rest_test_authorization.py)
        """
        # No users in the repo
        self.assert_users_count()
        # One user must be admin.
        assign_user_to_repo_group(
            self.admin_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=1)
        self.login(self.admin_user.username)

        # First part: assign group to user
        # Assign unexpected group will fail
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': 'foo'},
            username=self.author_user.username,
            expected_status=HTTP_400_BAD_REQUEST
        )
        # Assign real group to nonexistent user will fail
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': GroupTypes.REPO_ADMINISTRATOR},
            username='foo_username',
            expected_status=HTTP_404_NOT_FOUND
        )
        # Assign authors group
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': BaseGroupTypes.AUTHORS},
            username=self.author_user.username,
            reverse_str='repo-members-user-group-detail'
        )
        self.assert_users_count(admins=1, authors=1)
        # Repeating the same assignment has no effect
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': BaseGroupTypes.AUTHORS},
            username=self.author_user.username,
            reverse_str='repo-members-user-group-detail'
        )
        self.assert_users_count(admins=1, authors=1)
        # Assign curators group
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': BaseGroupTypes.CURATORS},
            username=self.curator_user.username,
            reverse_str='repo-members-user-group-detail'
        )
        self.assert_users_count(admins=1, curators=1, authors=1)
        # Assign admin group
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': BaseGroupTypes.ADMINISTRATORS},
            username=self.admin_user2.username,
            reverse_str='repo-members-user-group-detail'
        )
        self.assert_users_count(admins=2, curators=1, authors=1)
        # Assign admin group to curator user (user can have multiple groups)
        self.create_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            mem_dict={'group_type': BaseGroupTypes.ADMINISTRATORS},
            username=self.curator_user.username,
            reverse_str='repo-members-user-group-detail'
        )
        self.assert_users_count(admins=3, curators=1, authors=1)

        # Reset users configuration
        self.remove_all_users_from_repo()
        self.assert_users_count()
        assign_user_to_repo_group(
            self.admin_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=1)

        # Second part: assign user to group
        # Assign unexpected group will fail
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.author_user.username},
            group_type='foo',
            expected_status=HTTP_404_NOT_FOUND
        )
        # Assign real group to nonexistent user will fail
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': 'foo_username'},
            group_type=BaseGroupTypes.AUTHORS,
            expected_status=HTTP_400_BAD_REQUEST
        )
        # Assign user to authors group
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.author_user.username},
            group_type=BaseGroupTypes.AUTHORS,
            reverse_str='repo-members-group-user-detail'
        )
        self.assert_users_count(admins=1, authors=1)
        # Repeating the same assignment has no effect
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.author_user.username},
            group_type=BaseGroupTypes.AUTHORS,
            reverse_str='repo-members-group-user-detail'
        )
        self.assert_users_count(admins=1, authors=1)
        # Assign user to curators group
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.curator_user.username},
            group_type=BaseGroupTypes.CURATORS,
            reverse_str='repo-members-group-user-detail'
        )
        self.assert_users_count(admins=1, curators=1, authors=1)
        # Assign user to admins group
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.admin_user2.username},
            group_type=BaseGroupTypes.ADMINISTRATORS,
            reverse_str='repo-members-group-user-detail'
        )
        self.assert_users_count(admins=2, curators=1, authors=1)
        # Assign curator user to admin group (user can have multiple groups)
        self.create_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            mem_dict={'username': self.curator_user.username},
            group_type=BaseGroupTypes.ADMINISTRATORS,
            reverse_str='repo-members-group-user-detail'
        )
        self.assert_users_count(admins=3, curators=1, authors=1)

    def test_members_delete(self):
        """
        Members DELETE
        Testing only using an administrator used logged in.
        All the other kind of users don't have permissions to handle users.
        (tests for other users in rest_test_authorization.py)
        """
        # No users in the repo
        self.assert_users_count()
        # Populate repo groups.
        self.add_users_to_repo()
        # Add extra administrator
        assign_user_to_repo_group(
            self.admin_user2, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=2, curators=1, authors=1)
        self.login(self.admin_user2)

        # First part: delete group from user
        # Delete authors group
        self.delete_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            username=self.author_user.username,
            group_type=BaseGroupTypes.AUTHORS,
        )
        self.assert_users_count(admins=2, curators=1)
        # Delete curators group
        self.delete_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            username=self.curator_user.username,
            group_type=BaseGroupTypes.CURATORS,
        )
        self.assert_users_count(admins=2)
        # Delete administrators group
        self.delete_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            username=self.admin_user.username,
            group_type=BaseGroupTypes.ADMINISTRATORS,
        )
        self.assert_users_count(admins=1)
        # Trying to delete the last of administrators group will fail
        self.delete_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            username=self.admin_user2.username,
            group_type=BaseGroupTypes.ADMINISTRATORS,
            expected_status=HTTP_400_BAD_REQUEST
        )
        self.assert_users_count(admins=1)
        # Add back second admin
        assign_user_to_repo_group(
            self.admin_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=2)
        # Admin is able to delete self if there is another admin
        self.delete_member(
            urlfor='users',
            repo_slug=self.repo.slug,
            username=self.admin_user2.username,
            group_type=BaseGroupTypes.ADMINISTRATORS
        )
        self.assert_users_count(admins=1)

        # Reset users configuration
        # Populate repo groups.
        self.add_users_to_repo()
        # Add extra administrator
        assign_user_to_repo_group(
            self.admin_user2, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=2, curators=1, authors=1)

        # Second part: delete user from group
        # Delete user from authors group
        self.delete_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            username=self.author_user.username,
            group_type=BaseGroupTypes.AUTHORS,
        )
        self.assert_users_count(admins=2, curators=1)
        # Delete user from curators group
        self.delete_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            username=self.curator_user.username,
            group_type=BaseGroupTypes.CURATORS,
        )
        self.assert_users_count(admins=2)
        # Delete user from administrators group
        self.delete_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            username=self.admin_user.username,
            group_type=BaseGroupTypes.ADMINISTRATORS,
        )
        self.assert_users_count(admins=1)
        # Trying to delete the last of administrators group will fail
        self.delete_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            username=self.admin_user2.username,
            group_type=BaseGroupTypes.ADMINISTRATORS,
            expected_status=HTTP_400_BAD_REQUEST
        )
        self.assert_users_count(admins=1)
        # Add back second admin
        assign_user_to_repo_group(
            self.admin_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.assert_users_count(admins=2)
        # Admin is able to delete self if there is another admin
        self.delete_member(
            urlfor='groups',
            repo_slug=self.repo.slug,
            username=self.admin_user2.username,
            group_type=BaseGroupTypes.ADMINISTRATORS
        )
        self.assert_users_count(admins=1)


# pylint: disable=too-many-ancestors
class TestMembersAuthorization(RESTAuthTestCase):
    """Tests for member authorization via REST"""

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
