"""
Test the permissions
"""

from __future__ import unicode_literals

from django.test.testcases import TestCase

from roles.permissions import GroupTypes, RepoPermission


class TestRolePermission(TestCase):
    """
    Tests for the permissions
    """
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
        self.assertListEqual(
            RepoPermission.administrator_permissions(),
            [view_repo[0], import_course[0],
             manage_taxonomy[0], add_edit_metadata[0]]
        )
        self.assertListEqual(
            RepoPermission.curator_permissions(),
            [view_repo[0], import_course[0],
             manage_taxonomy[0], add_edit_metadata[0]]
        )
        self.assertListEqual(
            RepoPermission.author_permissions(),
            [view_repo[0], add_edit_metadata[0]]
        )
