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
from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404

from audit.models import BaseModel
from rest.util import default_slugify
from roles.api import roles_update_repo
from roles.permissions import RepoPermission
from lore.settings import LORE_PREVIEW_BASE_URL

log = logging.getLogger(__name__)

# defining the file path max length
FILE_PATH_MAX_LENGTH = 900
STATIC_ASSET_PREFIX = 'assets'
STATIC_ASSET_BASEPATH = STATIC_ASSET_PREFIX + '/{org}/{course_number}/{run}/'


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
    return (STATIC_ASSET_BASEPATH + '{filename}').format(
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
        # pylint: disable=missing-docstring,too-few-public-methods
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


class LearningResourceContentXml(BaseModel):
    """
    The content XML for a LearningResource.
    """
    content_xml = models.TextField()


class LearningResource(BaseModel):
    """
    The units that compose an edX course:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    course = models.ForeignKey(Course, related_name="resources")
    learning_resource_type = models.ForeignKey('LearningResourceType')
    static_assets = models.ManyToManyField(StaticAsset, blank=True)
    uuid = models.TextField()
    title = models.TextField()
    description = models.TextField(blank=True)
    _content_xml = models.TextField(db_column="content_xml", null=True)
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
    content_xml_model = models.ForeignKey(LearningResourceContentXml)

    @property
    def content_xml(self):
        """
        The content XML for a LearningResource.
        """
        return self.content_xml_model.content_xml


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
        """
        Handle slugs and groups.
        """
        is_update = False
        if self.id is None or self.name != get_object_or_404(
                Repository, id=self.id).name:
            # if it is an update of the repository, need the old slug
            if self.id is not None:
                is_update = True
                old_slug = get_object_or_404(Repository, id=self.id).slug
            self.slug = default_slugify(
                self.name,
                Repository._meta.model_name,
                lambda slug: Repository.objects.filter(slug=slug).exists()
            )
            # check if it's necessary to initialize the permissions
        new_repository = super(Repository, self).save(*args, **kwargs)
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


def get_preview_url(resource, org=None, course_number=None, run=None):
    """
    Create a preview URL. Accepts optional kwargs to prevent
    database lookups, especially for during search engine indexing.
    Args:
        resource (LearningResource): LearningResource
        org (unicode): resource.course.org
        run (unicode): resource.course.run
        course_number (unicode): resource.course.course_number
    Returns:
        url (unicode): Preview URL for LearningResource.
    """
    if org is None:
        org = resource.course.org
    if course_number is None:
        course_number = resource.course.course_number
    if run is None:
        run = resource.course.run
    key = "{org}/{course}/{run}".format(
        org=org,
        course=course_number,
        run=run,
    )

    if resource.url_name is None:
        path = "courseware"
        preview_id = ""
    else:
        path = "jump_to_id"
        preview_id = "/{0}".format(resource.url_name)

    url_format = '{base_url}courses/{key}/{path}{preview_id}'
    return url_format.format(
        base_url=LORE_PREVIEW_BASE_URL,
        path=urllib_parse.quote(path),
        key=urllib_parse.quote(key),
        preview_id=urllib_parse.quote(preview_id),
    )
