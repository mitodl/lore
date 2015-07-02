"""
Utility functions and classes for REST app
"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework.fields import BooleanField, empty

from roles.permissions import BaseGroupTypes


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


class CheckValidMemberParamMixin(object):
    """
    Validates the URL params for the members to return 404 in case
    something is not available.
    If everything is fine, it just returns None.
    """
    def dispatch(self, request, *args, **kwargs):
        """Pre dispatch"""
        username = self.kwargs.get('username')
        group_type = self.kwargs.get('group_type')
        if username is not None:
            get_object_or_404(User, username=username)
        if (group_type is not None and
                group_type not in BaseGroupTypes.all_base_groups()):
            raise Http404('Group type {} is not valid'.format(group_type))
        return super(
            CheckValidMemberParamMixin,
            self
        ).dispatch(request, *args, **kwargs)
