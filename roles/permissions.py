"""
Definition of Django custom permissions
"""

from __future__ import unicode_literals


class PermissionException(Exception):
    """Custom exception for permission"""


class InvalidGroupType(PermissionException):
    """Invalid group type"""


class InvalidBaseGroupType(PermissionException):
    """Invalid base group type"""


class BaseGroupTypes(object):
    """
    Basic group types
    """
    ADMINISTRATORS = "administrators"
    CURATORS = "curators"
    AUTHORS = "authors"

    @classmethod
    def all_base_groups(cls):
        """
        Return the basic group names
        """
        return [cls.ADMINISTRATORS, cls.CURATORS, cls.AUTHORS]

    @classmethod
    def is_base_group_type(cls, base_group_type):
        """
        Checks if the basic_group_type is an allowed one
        """
        return base_group_type in cls.all_base_groups()


class GroupTypes(object):
    """
    Definition of generic repository group names
    """
    RAW_GROUP_NAME = '{}_repo_{}'

    REPO_ADMINISTRATOR = RAW_GROUP_NAME.format(
        '{}', BaseGroupTypes.ADMINISTRATORS
    )
    REPO_CURATOR = RAW_GROUP_NAME.format('{}', BaseGroupTypes.CURATORS)
    REPO_AUTHOR = RAW_GROUP_NAME.format('{}', BaseGroupTypes.AUTHORS)

    _GROUP_ASSOC = {
        BaseGroupTypes.ADMINISTRATORS: REPO_ADMINISTRATOR,
        BaseGroupTypes.CURATORS: REPO_CURATOR,
        BaseGroupTypes.AUTHORS: REPO_AUTHOR
    }

    @classmethod
    def get_repo_groupname_by_base(cls, base_group_type):
        """
        Returns the basic group name from the repo name
        """
        try:
            return cls._GROUP_ASSOC[base_group_type]
        except KeyError:
            raise InvalidBaseGroupType


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
    manage_repo_users = ('manage_repo_users',
                         'Permission manage users for the repository')

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
            cls.manage_repo_users[0],
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
