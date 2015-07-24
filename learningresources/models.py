"""
Learning resources data model
"""

from __future__ import unicode_literals

import logging
# pylint currently has a bug which incorrectly flags this as an error
import six.moves.urllib.parse as urllib_parse  # pylint: disable=import-error

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404

from audit.models import BaseModel
from roles.api import roles_init_new_repo, roles_update_repo
from roles.permissions import RepoPermission
from lore.settings import LORE_PREVIEW_BASE_URL

log = logging.getLogger(__name__)

# defining the file path max length
FILE_PATH_MAX_LENGTH = 900
STATIC_ASSET_BASEPATH = 'assets/{org}/{course_number}/{run}/'


class FilePathLengthException(Exception):
    """Custom Exception to handle long file paths"""


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
    return (STATIC_ASSET_BASEPATH + '{filename}').format(
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
    asset = models.FileField(
        upload_to=static_asset_basepath,
        max_length=FILE_PATH_MAX_LENGTH
    )

    def save(self, *args, **kwargs):
        """
        Handle file length properly
        It seems that Django FileField does not enforce the length
        """
        if len(self.asset.name) > FILE_PATH_MAX_LENGTH:
            raise FilePathLengthException(
                'File path is more than {} characters long'.format(
                    FILE_PATH_MAX_LENGTH
                )
            )
        super(StaticAsset, self).save(*args, **kwargs)


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
    description = models.TextField(blank=True)
    content_xml = models.TextField()
    materialized_path = models.TextField()
    description_path = models.TextField(blank=True)
    url_path = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True)
    copyright = models.TextField()
    xa_nr_views = models.IntegerField(default=0)
    xa_nr_attempts = models.IntegerField(default=0)
    xa_avg_grade = models.FloatField(default=0)
    xa_histogram_grade = models.FloatField(default=0)
    url_name = models.TextField(null=True)

    def get_preview_url(self):
        """Create a preview URL."""
        key = "{org}/{course}/{run}".format(
            org=self.course.org,
            course=self.course.course_number,
            run=self.course.run,
        )

        if self.url_name is not None:
            url_format = 'courses/{key}/jump_to_id/{preview_id}'
            return LORE_PREVIEW_BASE_URL + urllib_parse.quote(
                url_format.format(
                    base_url=LORE_PREVIEW_BASE_URL,
                    key=key,
                    preview_id=self.url_name,
                )
            )
        else:
            url_format = 'courses/{key}/courseware'
            return LORE_PREVIEW_BASE_URL + urllib_parse.quote(
                url_format.format(
                    base_url=LORE_PREVIEW_BASE_URL,
                    key=key,
                )
            )


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
