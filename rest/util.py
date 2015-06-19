"""
Utility functions and classes for REST app
"""

from __future__ import unicode_literals


class LambdaDefault(object):
    """
    Provide a default field value given a function
    with a context for a parameter
    """

    def __init__(self, func):
        """Get function which can make use of context"""
        self.context = None
        self.func = func

    def set_context(self, serializer_field):
        """Grab context from serializer field"""
        self.context = serializer_field.context

    def __call__(self):
        """Pass context to function which contains view and request"""
        return self.func(self.context)
