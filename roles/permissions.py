"""
Definition of Django custom permissions
"""

from __future__ import unicode_literals


class GroupTypes(object):
    """
    Definition of generic group names
    """
    repo_administrator = '{}_repo_administrators'
    repo_curator = '{}_repo_curators'
    repo_author = '{}_repo_authors'


class RepoPermission(object):
    """
    Permissions for the repo objects
    Django permissions are defined as a tuple of (name, description)
    """
    view_repo = ('view_repo', 'Permission to view the repository')
    import_course = ('import_course',
                     'Permission to import course in repository')
    manage_taxonomy = ('manage_taxonomy',
                       'Permission to manage repository taxonomy')
    add_edit_metadata = ('add_edit_metadata',
                         'Permission to add or edit metadata')

    @classmethod
    def administrator_permissions(cls):
        """
        Administrator permissions
        """
        return [
            cls.view_repo[0],
            cls.import_course[0],
            cls.manage_taxonomy[0],
            cls.add_edit_metadata[0],
        ]

    @classmethod
    def curator_permissions(cls):
        """
        Curator permissions
        """
        return [
            cls.view_repo[0],
            cls.import_course[0],
            cls.manage_taxonomy[0],
            cls.add_edit_metadata[0],
        ]

    @classmethod
    def author_permissions(cls):
        """
        Author permissions
        """
        return [
            cls.view_repo[0],
            cls.add_edit_metadata[0],
        ]
