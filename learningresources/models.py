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

from audit.models import BaseModel
from roles.api import roles_init_new_repo, roles_update_repo
from roles.permissions import RepoPermission

log = logging.getLogger(__name__)


def static_asset_basepath(asset, filename):
    """
    Creates folder base path for given asset.

    Callback API defined by:
    https://docs.djangoproject.com/en/1.8/ref/models/fields/#django.db.models.FileField.upload_to
    Args:
        asset (StaticAsset): The model to create the name for.
        filename (unicode): The subpath and filename of ``asset.asset``
    Returns:
        (unicode): forward slash separated path to use below
            ``settings.MEDIA_ROOT``.
    """
    return 'assets/{org}/{course_number}/{run}/{filename}'.format(
        org=asset.course.org,
        course_number=asset.course.course_number,
        run=asset.course.run,
        filename=filename
    )


def course_asset_basepath(course, filename):
    """
    Returns folder base path for given path.

    Callback API defined by:
    https://docs.djangoproject.com/en/1.8/ref/models/fields/#django.db.models.FileField.upload_to
    Args:
        course (Course): The model to create the name for.
        filename (unicode): The subpath and filename of the asset.
    Returns:
        (unicode): forward slash separated path to use below
            ``settings.MEDIA_ROOT``.
    """
    return 'assets/{org}/{course_number}/{run}/{filename}'.format(
        org=course.org,
        course_number=course.course_number,
        run=course.run,
        filename=filename
    )


class Course(BaseModel):
    """
    A course on edX platform (MITx or residential).
    """
    repository = models.ForeignKey('Repository')
    org = models.TextField()
    course_number = models.TextField()
    run = models.TextField()
    imported_by = models.ForeignKey(User)

    class Meta:
        # pylint: disable=invalid-name,missing-docstring,too-few-public-methods
        unique_together = ("repository", "org", "course_number", "run")


class StaticAsset(BaseModel):
    """
    Holds static assets for a course (css, html, javascript, images, etc)
    """
    course = models.ForeignKey(Course)
    asset = models.FileField(upload_to=static_asset_basepath)


class LearningResource(BaseModel):
    """
    The units that compose an edX course:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    course = models.ForeignKey(Course)
    learning_resource_type = models.ForeignKey('LearningResourceType')
    static_assets = models.ManyToManyField(StaticAsset, blank=True)
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
class LearningResourceType(BaseModel):
    """
    Learning resource type:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Repository(BaseModel):
    """
    A collection of learning resources
    that come from (usually tightly-related) courses.
    """
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(User)

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

    class Meta:  # pylint: disable=missing-docstring
        permissions = (
            RepoPermission.view_repo,
            RepoPermission.import_course,
            RepoPermission.manage_taxonomy,
            RepoPermission.add_edit_metadata,
            RepoPermission.manage_repo_users,
        )
