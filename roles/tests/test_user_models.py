"""
Test the roles user models
"""

from __future__ import unicode_literals
from django.test.testcases import TestCase

from roles.user_models import UserGroup


class TestRoleUtils(TestCase):
    """
    Tests for the roles user models
    """
    def test_user_group_repr(self):
        """Test for UserGroup __repr__"""
        user_group = UserGroup('foo', 'bar')
        self.assertEqual(
            user_group.__repr__(),
            '<username:foo | group_type:bar>'
        )

    def test_user_group_eq_ne(self):
        """Test for UserGroup __eq__ and __ne__"""
        user_group1 = UserGroup('foo1', 'bar')
        user_group2 = UserGroup('foo1', 'bar')
        self.assertTrue(user_group1.__eq__(user_group2))
        self.assertFalse(user_group1.__ne__(user_group2))

        user_group2 = UserGroup('foo2', 'bar')
        self.assertFalse(user_group1.__eq__(user_group2))
        self.assertTrue(user_group1.__ne__(user_group2))

        user_group1 = UserGroup('foo1', 'bar1')
        user_group2 = UserGroup('foo1', 'bar2')
        self.assertFalse(user_group1.__eq__(user_group2))
        self.assertTrue(user_group1.__ne__(user_group2))

        # Making equal objects
        user_group2 = UserGroup('foo1', 'bar1')
        # Removing an attribute of the second object.
        user_group2.__dict__.pop('username')
        self.assertFalse(user_group1.__eq__(user_group2))
        self.assertTrue(user_group1.__ne__(user_group2))

        # define a different object
        class FooObject(object):
            """Foo object"""
            def __init__(self, foo_var):
                self.foo_var = foo_var

        user_group2 = FooObject('bar')
        self.assertFalse(user_group1.__eq__(user_group2))
