"""
Utility functions and classes for REST app
"""

from __future__ import unicode_literals

from rest_framework.fields import BooleanField, empty


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


class RequiredBooleanField(BooleanField):
    """Override Django REST Framework behavior where BooleanField is coerced
    to False even if required=True and value is missing from request"""

    def get_value(self, dictionary):
        """Override get_value to skip incorrect html.is_html_input check"""
        return dictionary.get(self.field_name, empty)
