"""
Utility functions for REST testing
"""

from __future__ import unicode_literals

from celery.backends.base import KeyValueStoreBackend


class FakeBackend(KeyValueStoreBackend):
    """
    Provide a fake key value store for Celery for testing purposes.
    """
    def __init__(self, *args, **kwargs):
        super(FakeBackend, self).__init__(*args, **kwargs)

        self.tasks = {}

    def get(self, key):
        return self.tasks.get(key)

    def set(self, key, value):
        self.tasks[key] = value
