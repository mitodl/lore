"""
Learning resources data model
"""

from __future__ import unicode_literals

import logging

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404

from roles.api import roles_init_new_repo, roles_update_repo
from roles.permissions import RepoPermission

log = logging.getLogger(__name__)


class Course(models.Model):
    """
    A course on edX platform (MITx or residential).
    """
    repository = models.ForeignKey('Repository')
    org = models.TextField()
    course_number = models.TextField()
    run = models.TextField()
    import_date = models.DateField(auto_now_add=True)
    imported_by = models.ForeignKey(User)

    class Meta:
        # pylint: disable=invalid-name,missing-docstring,too-few-public-methods
        unique_together = ("repository", "org", "course_number", "run")


class LearningResource(models.Model):
    """
    The units that compose an edX course:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    course = models.ForeignKey(Course)
    learning_resource_type = models.ForeignKey('LearningResourceType')
    uuid = models.TextField()
    title = models.TextField()
    description = models.TextField()
    content_xml = models.TextField()
    materialized_path = models.TextField()
    url_path = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True)
    copyright = models.TextField()
    xa_nr_views = models.IntegerField(default=0)
    xa_nr_attempts = models.IntegerField(default=0)
    xa_avg_grade = models.FloatField(default=0)
    xa_histogram_grade = models.FloatField(default=0)


@python_2_unicode_compatible
class LearningResourceType(models.Model):
    """
    Learning resource type:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Repository(models.Model):
    """
    A collection of learning resources
    that come from (usually tightly-related) courses.
    """
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def has_resources(self):
        """Are any LearningResources uploaded for this repository?"""
        return LearningResource.objects.filter(
            course__repository__id=self.id).exists()

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle slugs and groups"""
        is_create = False
        is_update = False
        if self.id is None or self.name != get_object_or_404(
                Repository, id=self.id).name:
            # if it is an update of the repository, need the old slug
            if self.id is not None:
                is_update = True
                old_slug = get_object_or_404(Repository, id=self.id).slug
            slug = slugify(self.name)
            count = 1
            while Repository.objects.filter(slug=slug).exists():
                slug = "{0}{1}".format(slugify(self.name), count)
                count += 1
            self.slug = slug
            # check if it's necessary to initialize the permissions
            if self.id is None:
                is_create = True
        new_repository = super(Repository, self).save(*args, **kwargs)
        if is_create:
            roles_init_new_repo(self)
        if is_update:
            roles_update_repo(self, old_slug)
        return new_repository

    class Meta:
        # pylint: disable=missing-docstring
        permissions = (
            RepoPermission.view_repo,
            RepoPermission.import_course,
            RepoPermission.manage_taxonomy,
            RepoPermission.add_edit_metadata,
        )
