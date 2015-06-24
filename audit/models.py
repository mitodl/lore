"""A base class for all models with audit fields."""

from django.db import models


class BaseModel(models.Model):
    """A models.Model with audit fields."""
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Do not create a database table for BaseModel."""
        abstract = True
