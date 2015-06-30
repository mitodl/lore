"""
User data models (mostly used for the Rest Framework)
"""
from __future__ import unicode_literals


class UserGroup(object):
    """
    Class defining the relationship between an user name and a basic group type
    """
    def __init__(self, username, group_type):
        self.username = username
        self.group_type = group_type

    def __repr__(self):
        return "<username:{username} | group_type:{group_type}>".format(
            username=self.username,
            group_type=self.group_type
        )

    def __eq__(self, other):
        try:
            return (isinstance(other, UserGroup) and
                    self.username == other.username and
                    self.group_type == other.group_type)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.username, self.group_type))
