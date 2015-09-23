"""
Helper functions for using the models, so external
apps don't tie functionality to internal implementation.
"""

from __future__ import unicode_literals

import logging
from os import walk, sep
from os.path import join

from django.contrib.auth.models import User
from django.core.files import File
from django.db import transaction

from guardian.shortcuts import get_objects_for_user, get_perms

from learningresources.models import (
    Course, Repository, LearningResource, LearningResourceType, StaticAsset
)
from roles.permissions import RepoPermission

log = logging.getLogger(__name__)


class LearningResourceException(Exception):
    """Base class for our custom exceptions."""
    pass


class PermissionDenied(LearningResourceException):
    """
    Raised by the API when the requested item exists, but the
    user is not allowed to access it.
    """
    pass


class NotFound(LearningResourceException):
    """Raised by the API when the item requested does not exist."""
    pass


def create_course(org, repo_id, course_number, run, user_id):
    """
    Add a course to the database.

    Args:
        org (unicode): Organization
        repo_id (int): Repository id
        course_number (unicode): Course number
        run (unicode): Run
        user_id (int): Primary key of user creating the course
    Raises:
        ValueError: Duplicate course
    Returns:
        course (learningresources.models.Course): The created course

    """
    # Check on unique values before attempting a get_or_create, because
    # items such as date_created  will always make it non-unique.
    unique = {
        "org": org, "course_number": course_number, "run": run,
        "repository_id": repo_id,
    }
    if Course.objects.filter(**unique).exists():
        raise ValueError("Duplicate course")
    kwargs = {
        "org": org,
        "course_number": course_number,
        "run": run,
        'imported_by_id': user_id,
        "repository_id": repo_id,
    }
    with transaction.atomic():
        course, _ = Course.objects.get_or_create(**kwargs)
    return course


# pylint: disable=too-many-arguments
def create_resource(
        course, parent, resource_type, title, content_xml, mpath, url_name,
        dpath
):
    """
    Create a learning resource.

    Args:
        course (learningresources.models.Course): Course
        parent (learningresources.models.LearningResource):
            Parent LearningResource
        resource_type (unicode): Name of LearningResourceType
        title (unicode): Title of resource
        content_xml (unicode): XML
        mpath (unicode): Materialized path
        url_name (unicode): Resource identifier
        dpath (unicode): Description path

    Returns:
        resource (learningresources.models.LearningResource):
            New LearningResource
    """
    params = {
        "course": course,
        "learning_resource_type_id": type_id_by_name(resource_type),
        "title": title,
        "content_xml": content_xml,
        "materialized_path": mpath,
        "url_name": url_name,
        "description_path": dpath,
    }
    if parent is not None:
        params["parent_id"] = parent.id
    with transaction.atomic():
        return LearningResource.objects.create(**params)


def type_id_by_name(name):
    """
    Get or create a LearningResourceType by name.

    This would do fewer queries if it did all the lookups up front, but
    this is simpler to read and understand and still prevents most lookups.
    Also, it can't prevent inserts, so it's never guaranteed to be just
    a single query.

    Args:
        name (unicode): LearningResourceType.name
    Returns:
        type_id (int): Primary key of learningresources.LearningResourceType
    """
    with transaction.atomic():
        obj, _ = LearningResourceType.objects.get_or_create(name=name.lower())
        return obj.id


def get_repos(user_id):
    """
    Get all repositories a user may access.

    Args:
        user_id (int): Primary key of user
    Returns:
        repos (query set of learningresource.Repository): Repositories
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise PermissionDenied(
            "user does not have permission for this repository"
        )
    return get_objects_for_user(
        user,
        RepoPermission.view_repo[0],
        klass=Repository
    )


def get_repo(repo_slug, user_id):
    """
    Get repository for a user if s/he can access it.
    Returns a repository object if it exists or
    * raises a 404 if the object does not exist
    * raises a 403 if the object exists but the user doesn't have permission

    Args:
        repo_slug (unicode): Repository slug
        user_id (int): Primary key of user
    Returns:
        repo (learningresource.Repository): Repository
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise PermissionDenied(
            "user does not have permission for this repository")
    try:
        repo = Repository.objects.get(slug=repo_slug)
    except Repository.DoesNotExist:
        raise NotFound()

    if RepoPermission.view_repo[0] in get_perms(user, repo):
        return repo
    raise PermissionDenied("user does not have permission for this repository")


def create_repo(name, description, user_id):
    """
    Create a new repository.

    Args:
        name (unicode): Repository name
        description (unicode): Repository description
        user_id (int): User ID of repository creator
    Returns:
        repo (learningresources.Repository): Newly-created repository
    """
    with transaction.atomic():
        return Repository.objects.create(
            name=name, description=description,
            created_by_id=user_id,
        )


def get_resources(repo_id):
    """
    Get resources from a repository ordered by title.

    Args:
        repo_id (int): Primary key of the repository
    Returns:
        list (list of learningresources.LearningResource): List of resources
    """
    return LearningResource.objects.select_related(
        "learning_resource_type", "course__repository").filter(
            course__repository__id=repo_id).order_by("title")


def get_resource(resource_id, user_id):
    """
    Get single resource.

    Args:
        resource_id (int): Primary key of the LearningResource
        user_id (int): Primary key of the user requesting the resource
    Returns:
        resource (learningresources.LearningResource): Resource
        May be None if the resource does not exist or the user does
        not have permissions.
    """
    try:
        resource = LearningResource.objects.get(id=resource_id)
    except LearningResource.DoesNotExist:
        raise NotFound("LearningResource not found")
    # This will raise PermissionDenied if it fails.
    get_repo(resource.course.repository.slug, user_id)
    return resource


def create_static_asset(course_id, handle):
    """
    Create a static asset.
    Args:
        course_id (int): learningresources.models.Course pk
        handle (django.core.files.File): file handle
    Returns:
        learningresources.models.StaticAsset
    """
    with transaction.atomic():
        return StaticAsset.objects.create(course_id=course_id, asset=handle)


def _subs_filename(subs_id, lang='en'):
    """
    Generate proper filename for storage.

    Function copied from:
    edx-platform/common/lib/xmodule/xmodule/video_module/transcripts_utils.py

    Args:
        subs_id (str): Subs id string
        lang (str): Locale language (optional) default: en

    Returns:
        filename (str): Filename of subs file
    """
    if lang in ('en', "", None):
        return u'subs_{0}.srt.sjson'.format(subs_id)
    else:
        return u'{0}_subs_{1}.srt.sjson'.format(lang, subs_id)


def get_video_sub(xml):
    """
    Get subtitle IDs from <video> XML.

    Args:
        xml (lxml.etree): xml for a LearningResource
    Returns:
        sub string: subtitle string
    """
    subs = xml.xpath("@sub")
    # It's not possible to have more than one.
    if len(subs) == 0:
        return ""
    return _subs_filename(subs[0])


def import_static_assets(course, path):
    """
    Upload all assets and create model records of them for a given
    course and path.

    Args:
        course (learningresources.models.Course): Course to add assets to.
        path (unicode): course specific path to extracted OLX tree.
    Returns:
        None
    """
    for root, _, files in walk(path):
        for name in files:
            with open(join(root, name), 'rb') as open_file:
                django_file = File(open_file)
                # Remove base path from file name
                name = join(root, name).replace(path + sep, '', 1)
                django_file.name = name
                create_static_asset(course.id, django_file)


def update_xanalytics(data):
    """
    Update xanalytics fields for a LearningResource.
    Args:
        data (dict): dict from JSON file from xanalytics
    Returns:
        count (int): number of records updated
    """
    vals = data.get("module_medata", [])
    course_number = data.get("course_id", "")
    count = 0
    for rec in vals:
        resource_key = rec.pop("module_id")
        count = LearningResource.objects.filter(
            uuid=resource_key,
            course__course_number=course_number,

        ).update(**rec)
        if count is None:
            count = 0
    return count


def join_description_paths(*args):
    """
    Helper function to format the description path.
    Args:
        args (unicode): description path
    Returns:
        unicode: Formatted dpath
    """
    return ' / '.join([dpath for dpath in args if dpath != ''])


def update_description_path(resource, force_parent_update=False):
    """
    Updates the specified learning resource description path
    based on the current title and the parent's description path
    Args:
        resource (learningresources.models.LearningResource): LearningResource
        force_parent_update (boolean): force parent update
    Returns:
        None
    """
    description_path = ''
    if resource.parent is None:
        description_path = join_description_paths(resource.title)
    else:
        # if the parent doesn't have a description_path update first the parent
        if resource.parent.description_path == '' or force_parent_update:
            update_description_path(resource.parent, force_parent_update)
        # the current description path is
        # the parent's one plus the current title
        description_path = join_description_paths(
            resource.parent.description_path,
            resource.title
        )
    resource.description_path = description_path
    resource.save()
