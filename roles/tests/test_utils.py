"""
Test the roles utils
"""

from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils.text import slugify
from guardian.shortcuts import get_perms
from mock import patch

from learningresources.api import create_repo
from learningresources.tests.base import LoreTestCase
from roles.permissions import RepoPermission, GroupTypes
from roles import utils


class TestRoleUtils(LoreTestCase):
    """
    Tests for the roles Utils
    """
    def __init__(self, *args, **kwargs):
        super(TestRoleUtils, self).__init__(*args, **kwargs)
        self.repo_name = 'my little+test repo'
        self.repo_desc = 'test description'
        self.repo_slug = slugify(self.repo_name)

        self.group_admin = GroupTypes.REPO_ADMINISTRATOR.format(self.repo_slug)
        self.group_curator = GroupTypes.REPO_CURATOR.format(self.repo_slug)
        self.group_author = GroupTypes.REPO_AUTHOR.format(self.repo_slug)

    def check_group_permission(self, repo, group, expected_permissions):
        """
        helper function
        """
        self.assertListEqual(
            sorted(get_perms(group, repo)),
            sorted(expected_permissions)
        )

    def test_sync_permissions(self):
        """
        test the syncpermission
        """
        repo = create_repo(self.repo_name, self.repo_desc, self.user.id)

        # Get default permissions before wiping.
        admin = Group.objects.get(name=self.group_admin)
        self.check_group_permission(
            repo,
            admin,
            RepoPermission.administrator_permissions()
        )
        with patch.object(utils, 'roles_init_new_repo') as mock_method:
            mock_method.return_value = None
            utils.sync_groups_permissions()
        # Get default permissions after wiping.
        self.check_group_permission(
            repo,
            admin,
            []
        )
        # Restore permissions the first call of sync_groups_permissions
        # will not do anything because the permissions have been already wiped.
        utils.sync_groups_permissions()
        self.check_group_permission(
            repo,
            admin,
            RepoPermission.administrator_permissions()
        )

    # pylint: disable=no-self-use
    def test_sync_permissions_command(self):
        """
        tests the sync_permission via manage.py command
        """
        with patch.object(utils, 'sync_groups_permissions') as mock_method:
            mock_method.return_value = None
            call_command('sync_permissions')
            mock_method.assert_called_with()
