"""
Test the roles APIs
"""

from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.utils.text import slugify
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_perms
from mock import patch

from learningresources.api import create_repo
from learningresources.models import Repository
from learningresources.tests.base import LoreTestCase
from roles import api
from roles.permissions import RepoPermission, GroupTypes, BaseGroupTypes
from roles.user_models import UserGroup


class TestRoleApi(LoreTestCase):
    """
    Tests for the roles APIs
    roles_init_new_repo is tested indirectly from
    the repository model where it is called
    """
    # there are too many self assignment in the init: disabling the check
    # pylint: disable=too-many-instance-attributes, invalid-name
    # pylint: disable=protected-access
    def __init__(self, *args, **kwargs):
        super(TestRoleApi, self).__init__(*args, **kwargs)
        self.repo_name = 'my little+test repo'
        self.repo_desc = 'test description'
        self.repo_slug = slugify(self.repo_name)
        self.repo_name2 = 'other test repo'
        self.repo_desc2 = 'other test description'
        self.repo_slug2 = slugify(self.repo_name2)
        self.group_admin = GroupTypes.REPO_ADMINISTRATOR.format(self.repo_slug)
        self.group_curator = GroupTypes.REPO_CURATOR.format(self.repo_slug)
        self.group_author = GroupTypes.REPO_AUTHOR.format(self.repo_slug)
        self.group_admin2 = GroupTypes.REPO_ADMINISTRATOR.format(
            self.repo_slug2)
        self.group_curator2 = GroupTypes.REPO_CURATOR.format(self.repo_slug2)
        self.group_author2 = GroupTypes.REPO_AUTHOR.format(self.repo_slug2)

    def sort_user_group(self, user_group_list):
        """
        Helper function to sort custom UserGroup objects
        """
        # pylint: disable=no-self-use
        return sorted(
            user_group_list,
            key=lambda x: x.username
        )

    def test_roles_init_new_repo_1(self):
        """
        No group before the repo is created
        """
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(name=self.group_admin)
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(name=self.group_curator)
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(name=self.group_author)

    def test_roles_init_new_repo_2(self):
        """
        Groups and permissions created by the repo creations
        """
        repo = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        admin = Group.objects.get(name=self.group_admin)
        curator = Group.objects.get(name=self.group_curator)
        author = Group.objects.get(name=self.group_author)
        checker_admin = ObjectPermissionChecker(admin)
        self.assertListEqual(
            sorted(checker_admin.get_perms(repo)),
            sorted(RepoPermission.administrator_permissions())
        )
        checker_curator = ObjectPermissionChecker(curator)
        self.assertListEqual(
            sorted(checker_curator.get_perms(repo)),
            sorted(RepoPermission.curator_permissions())
        )
        checker_author = ObjectPermissionChecker(author)
        self.assertListEqual(
            sorted(checker_author.get_perms(repo)),
            sorted(RepoPermission.author_permissions())
        )

    def test_roles_init_new_repo_fake_permission_admin(self):
        """
        Non existing permissions for admin
        """
        with patch.object(api.RepoPermission,
                          'administrator_permissions') as mock_method:
            mock_method.return_value = ['fake_permission']
            repo = create_repo(
                name=self.repo_name,
                description=self.repo_desc,
                user_id=self.user.id,
            )
            admin = Group.objects.get(name=self.group_admin)
            self.assertListEqual(
                get_perms(admin, repo),
                []
            )

    def test_roles_init_new_repo_fake_permission_curator(self):
        """
        Non existing permissions for curator
        """
        with patch.object(api.RepoPermission,
                          'curator_permissions') as mock_method:
            mock_method.return_value = ['fake_permission']
            repo = create_repo(
                name=self.repo_name,
                description=self.repo_desc,
                user_id=self.user.id,
            )
            curator = Group.objects.get(name=self.group_curator)
            self.assertListEqual(
                get_perms(curator, repo),
                []
            )

    def test_roles_init_new_repo_fake_permission_author(self):
        """
        Non existing permissions for author
        """
        with patch.object(api.RepoPermission,
                          'author_permissions') as mock_method:
            mock_method.return_value = ['fake_permission']
            repo = create_repo(
                name=self.repo_name,
                description=self.repo_desc,
                user_id=self.user.id,
            )
            author = Group.objects.get(name=self.group_author)
            self.assertListEqual(
                get_perms(author, repo),
                []
            )

    def test_roles_update_repo_1(self):
        """
        Test update repo name
        """
        repo = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        # this is to test that the repo created groups with the right name
        # they will raise an exception if they fail
        Group.objects.get(name=self.group_admin)
        Group.objects.get(name=self.group_curator)
        Group.objects.get(name=self.group_author)

        repo.name = self.repo_name2
        repo.save()
        self.assertEqual(repo.name, self.repo_name2)

        # this is to test that the repo updated groups with the right name
        # they will raise an exception if they fail
        Group.objects.get(name=self.group_admin2)
        Group.objects.get(name=self.group_curator2)
        Group.objects.get(name=self.group_author2)
        # test the group with old name do not exist
        self.assertRaises(Group.DoesNotExist, Group.objects.get,
                          name=self.group_admin)
        self.assertRaises(Group.DoesNotExist, Group.objects.get,
                          name=self.group_curator)
        self.assertRaises(Group.DoesNotExist, Group.objects.get,
                          name=self.group_author)

    def test_roles_update_repo_2(self):
        """
        Test update repo name with same name
        """
        repo = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        api.roles_update_repo(repo, self.repo_slug)
        # this is to test that the repo created groups with the right name
        # they will raise an exception if they fail
        Group.objects.get(name=self.group_admin)
        Group.objects.get(name=self.group_curator)
        Group.objects.get(name=self.group_author)

    def test_assign_user_group_1(self):
        """
        Test for api.assign_user_to_repo_group
        check situation before use of helper function
        """
        _ = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        admin = Group.objects.get(name=self.group_admin)
        curator = Group.objects.get(name=self.group_curator)
        author = Group.objects.get(name=self.group_author)
        self.assertNotIn(self.user, admin.user_set.all())
        self.assertNotIn(self.user, curator.user_set.all())
        self.assertNotIn(self.user, author.user_set.all())

    def test_assign_user_group_2(self):
        """
        Test for api.assign_user_to_repo_group
        """
        repo = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        admin = Group.objects.get(name=self.group_admin)
        curator = Group.objects.get(name=self.group_curator)
        author = Group.objects.get(name=self.group_author)

        api.assign_user_to_repo_group(
            self.user,
            repo,
            group_type=GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertIn(self.user, admin.user_set.all())
        self.assertNotIn(self.user, curator.user_set.all())
        self.assertNotIn(self.user, author.user_set.all())
        admin.user_set.clear()

        api.assign_user_to_repo_group(
            self.user,
            repo,
            group_type=GroupTypes.REPO_CURATOR
        )
        self.assertNotIn(self.user, admin.user_set.all())
        self.assertIn(self.user, curator.user_set.all())
        self.assertNotIn(self.user, author.user_set.all())
        curator.user_set.clear()

        api.assign_user_to_repo_group(
            self.user,
            repo,
            group_type=GroupTypes.REPO_AUTHOR
        )
        self.assertNotIn(self.user, admin.user_set.all())
        self.assertNotIn(self.user, curator.user_set.all())
        self.assertIn(self.user, author.user_set.all())
        author.user_set.clear()

    def test_remove_user_from_group(self):
        """
        Test for api.remove_user_from_repo_group
        """
        repo = Repository.objects.create(
            name=self.repo_name,
            description=self.repo_desc,
            created_by=self.user
        )
        admin = Group.objects.get(name=self.group_admin)

        api.assign_user_to_repo_group(
            self.user,
            repo,
            group_type=GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertIn(self.user, admin.user_set.all())

        api.remove_user_from_repo_group(
            self.user,
            repo,
            group_type=GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertNotIn(self.user, admin.user_set.all())

    def test_clear_permissions(self):
        """
        Test for roles_clear_repo_permissions
        """
        self.assertListEqual(
            sorted(get_perms(self.user, self.repo)),
            sorted(RepoPermission.administrator_permissions())
        )
        api.roles_clear_repo_permissions(self.repo)
        self.assertListEqual(
            get_perms(self.user, self.repo),
            []
        )

    def test_list_users_in_repo_no_base_group_type_specified(self):
        """
        Test for list_users_in_repo
        """
        self.assertListEqual(
            api.list_users_in_repo(self.repo),
            [
                UserGroup(self.user.username, BaseGroupTypes.ADMINISTRATORS)
            ]
        )
        # Remove the user from the administrators.
        api.remove_user_from_repo_group(
            self.user,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        # No users in the repo.
        self.assertListEqual(
            api.list_users_in_repo(self.repo),
            []
        )
        # Add user to the curators.
        api.assign_user_to_repo_group(
            self.user,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        self.assertListEqual(
            api.list_users_in_repo(self.repo),
            [
                UserGroup(self.user.username, BaseGroupTypes.CURATORS)
            ]
        )
        # Add user back to the administrators.
        api.assign_user_to_repo_group(
            self.user,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertListEqual(
            self.sort_user_group(
                api.list_users_in_repo(self.repo)
            ),
            self.sort_user_group(
                [
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.ADMINISTRATORS
                    ),
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.CURATORS
                    )
                ]
            )
        )
        # Add another user to the authors.
        api.assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        self.assertListEqual(
            self.sort_user_group(
                api.list_users_in_repo(self.repo)
            ),
            self.sort_user_group(
                [
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.ADMINISTRATORS
                    ),
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.CURATORS
                    ),
                    UserGroup(
                        self.user_norepo.username,
                        BaseGroupTypes.AUTHORS
                    )
                ]
            )
        )
        # Adding again the same user in the same group
        # will not create multiple instances.
        api.assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_AUTHOR
        )
        self.assertListEqual(
            self.sort_user_group(
                api.list_users_in_repo(self.repo)
            ),
            self.sort_user_group(
                [
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.ADMINISTRATORS
                    ),
                    UserGroup(
                        self.user.username,
                        BaseGroupTypes.CURATORS
                    ),
                    UserGroup(
                        self.user_norepo.username,
                        BaseGroupTypes.AUTHORS
                    )
                ]
            )
        )

    def test_list_users_in_repo_base_group_type_specified(self):
        """
        Test for list_users_in_repo
        """
        self.assertListEqual(
            api.list_users_in_repo(self.repo),
            [
                UserGroup(self.user.username, BaseGroupTypes.ADMINISTRATORS)
            ]
        )
        self.assertListEqual(
            api.list_users_in_repo(self.repo, BaseGroupTypes.ADMINISTRATORS),
            [
                UserGroup(self.user.username, BaseGroupTypes.ADMINISTRATORS)
            ]
        )
        self.assertListEqual(
            api.list_users_in_repo(self.repo, BaseGroupTypes.CURATORS),
            []
        )
        self.assertListEqual(
            api.list_users_in_repo(self.repo, BaseGroupTypes.AUTHORS),
            []
        )

    def test_list_users_in_repo_invalid_group_type_specified(self):
        """
        Test for list_users_in_repo
        """
        self.assertRaises(
            api.InvalidGroupType,
            lambda: api.list_users_in_repo(self.repo, 'foo_type')
        )

    def test_is_last_admin_in_repo(self):
        """
        Test for is_last_admin_in_repo
        """
        # By default the repo creator is also administrator
        self.assertTrue(
            api.is_last_admin_in_repo(self.user, self.repo)
        )
        # Add another user to the administrators.
        api.assign_user_to_repo_group(
            self.user_norepo,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertFalse(
            api.is_last_admin_in_repo(self.user, self.repo)
        )
        # Remove the first user from the administrators.
        api.remove_user_from_repo_group(
            self.user,
            self.repo,
            GroupTypes.REPO_ADMINISTRATOR
        )
        # Add user to the curators.
        api.assign_user_to_repo_group(
            self.user,
            self.repo,
            GroupTypes.REPO_CURATOR
        )
        # The user is not the last of the admins because he is not admin
        self.assertFalse(
            api.is_last_admin_in_repo(self.user, self.repo)
        )
        # The other user is indeed the last admin
        self.assertTrue(
            api.is_last_admin_in_repo(self.user_norepo, self.repo)
        )
