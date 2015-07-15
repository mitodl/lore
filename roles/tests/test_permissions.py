"""
Test the permissions
"""

from __future__ import unicode_literals

from django.test.testcases import TestCase

from roles.permissions import (
    InvalidBaseGroupType,
    GroupTypes,
    BaseGroupTypes,
    RepoPermission
)


class TestRolePermission(TestCase):
    """
    Tests for the permissions
    """
    # pylint: disable=protected-access
    def test_base_group_types(self):
        """
        Checks basic repo group types
        """
        self.assertEqual(
            BaseGroupTypes.ADMINISTRATORS,
            'administrators'
        )
        self.assertEqual(
            BaseGroupTypes.CURATORS,
            'curators'
        )
        self.assertEqual(
            BaseGroupTypes.AUTHORS,
            'authors'
        )

    def test_all_base_group_names(self):
        """
        Checks all_basic_group_names method
        """
        self.assertEqual(
            sorted(BaseGroupTypes.all_base_groups()),
            sorted(
                [
                    BaseGroupTypes.ADMINISTRATORS,
                    BaseGroupTypes.CURATORS,
                    BaseGroupTypes.AUTHORS
                ]
            )
        )

    def test_is_base_group_type(self):
        """
        Checks is_repo_group_type method
        """
        self.assertTrue(
            BaseGroupTypes.is_base_group_type(
                BaseGroupTypes.ADMINISTRATORS
            )
        )
        self.assertTrue(
            BaseGroupTypes.is_base_group_type(
                BaseGroupTypes.CURATORS
            )
        )
        self.assertTrue(
            BaseGroupTypes.is_base_group_type(
                BaseGroupTypes.AUTHORS
            )
        )
        self.assertFalse(BaseGroupTypes.is_base_group_type('foo'))

    def test_group_types(self):
        """
        Checks repo group types
        """
        self.assertEqual(
            GroupTypes.REPO_ADMINISTRATOR,
            '{}_repo_administrators'
        )
        self.assertEqual(
            GroupTypes.REPO_CURATOR,
            '{}_repo_curators'
        )
        self.assertEqual(
            GroupTypes.REPO_AUTHOR,
            '{}_repo_authors'
        )

    def test_raw_group_name(self):
        """
        Checks base string for group name creation
        """
        self.assertEqual(
            GroupTypes.RAW_GROUP_NAME,
            '{}_repo_{}'
        )

    def test_group_assoc(self):
        """
        Checks group type to basic name association
        """
        self.assertEqual(len(GroupTypes._GROUP_ASSOC), 3)
        self.assertEqual(
            GroupTypes._GROUP_ASSOC.get(BaseGroupTypes.ADMINISTRATORS),
            GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertEqual(
            GroupTypes._GROUP_ASSOC.get(BaseGroupTypes.CURATORS),
            GroupTypes.REPO_CURATOR
        )
        self.assertEqual(
            GroupTypes._GROUP_ASSOC.get(BaseGroupTypes.AUTHORS),
            GroupTypes.REPO_AUTHOR
        )

    def test_get_repo_groupname_by_base(self):
        """
        Checks get_repo_groupname_by_base method
        """
        self.assertEqual(
            GroupTypes.get_repo_groupname_by_base(
                BaseGroupTypes.ADMINISTRATORS
            ),
            GroupTypes.REPO_ADMINISTRATOR
        )
        self.assertEqual(
            GroupTypes.get_repo_groupname_by_base(
                BaseGroupTypes.CURATORS
            ),
            GroupTypes.REPO_CURATOR
        )
        self.assertEqual(
            GroupTypes.get_repo_groupname_by_base(
                BaseGroupTypes.AUTHORS
            ),
            GroupTypes.REPO_AUTHOR
        )
        self.assertRaises(
            InvalidBaseGroupType,
            lambda: GroupTypes.get_repo_groupname_by_base('foo')
        )

    def test_repo_permissions(self):
        """
        Checks repo permissions
        """
        view_repo = ('view_repo', 'Permission to view the repository')
        import_course = ('import_course',
                         'Permission to import course in repository')
        manage_taxonomy = ('manage_taxonomy',
                           'Permission to manage repository taxonomy')
        add_edit_metadata = ('add_edit_metadata',
                             'Permission to add or edit metadata')
        manage_repo_users = ('manage_repo_users',
                             'Permission manage users for the repository')
        self.assertEqual(
            RepoPermission.view_repo,
            view_repo
        )
        self.assertEqual(
            RepoPermission.import_course,
            import_course
        )
        self.assertEqual(
            RepoPermission.manage_taxonomy,
            manage_taxonomy
        )
        self.assertEqual(
            RepoPermission.add_edit_metadata,
            add_edit_metadata
        )
        self.assertEqual(
            RepoPermission.manage_repo_users,
            manage_repo_users
        )
        self.assertListEqual(
            RepoPermission.administrator_permissions(),
            [
                view_repo[0],
                import_course[0],
                manage_taxonomy[0],
                add_edit_metadata[0],
                manage_repo_users[0]
            ]
        )
        self.assertListEqual(
            RepoPermission.curator_permissions(),
            [
                view_repo[0],
                import_course[0],
                manage_taxonomy[0],
                add_edit_metadata[0]
            ]
        )
        self.assertListEqual(
            RepoPermission.author_permissions(),
            [
                view_repo[0],
                add_edit_metadata[0]
            ]
        )
