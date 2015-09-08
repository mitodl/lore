"""
Import OLX data into LORE.
"""

from __future__ import unicode_literals

from bs4 import BeautifulSoup
from shutil import rmtree
import logging
from tempfile import mkdtemp
from os.path import join, exists, isdir
from os import listdir

from archive import Archive, ArchiveException
from django.core.files import File
from django.core.files.storage import default_storage
from lxml import etree
from xbundle import XBundle, DESCRIPTOR_TAGS

from importer.tasks import populate_xanalytics_fields
from learningresources.api import (
    create_course,
    create_resource,
    import_static_assets,
    create_static_asset,
    get_video_sub,
    join_description_paths,
    get_resources,
)
from learningresources.models import StaticAsset, course_asset_basepath
from search.utils import index_resources

log = logging.getLogger(__name__)


def import_course_from_file(filename, repo_id, user_id):
    """
    Import OLX archive from .zip or tar.gz.

    Imports from a file and then deletes that file.
    A valid OLX archive has a single occurrence of the file course.xml in its
    root directory, or no course.xml in its root and a single occurrence of
    course.xml in one or more of the root directory's children.

    Args:
        filename (unicode): Path to archive file (zip or .tar.gz)
        repo_id (int): Primary key of repository course belongs to
        user_id (int): Primary key of user importing the course
    Returns:
        None
    Raises:
        ValueError: Unable to extract or read archive contents.
    """
    tempdir = mkdtemp()

    # HACK: Have to patch in "seekable" attribute for python3 and tar
    # See: https://code.djangoproject.com/ticket/24963#ticket. Remove
    # when updating to Django 1.9
    def seekable():
        """Hacked seekable for django storage to work in python3"""
        return True
    try:
        course_archive = default_storage.open(filename)
        course_archive.seekable = seekable
        try:
            Archive(
                course_archive
            ).extract(to_path=tempdir, method="safe")
        except ArchiveException as ex:
            log.debug("failed to extract: %s", ex)
            log.exception('Archive exception occurred')
            raise ValueError("Invalid OLX archive, unable to extract.")
        course_imported = False
        if "course.xml" in listdir(tempdir):
            import_course_from_path(tempdir, repo_id, user_id)
            course_imported = True
        else:
            for path in listdir(tempdir):
                if exists(join(tempdir, path, 'course.xml')):
                    import_course_from_path(
                        join(tempdir, path), repo_id, user_id
                    )
                    course_imported = True
        if course_imported is False:
            raise ValueError("Invalid OLX archive, no courses found.")
    finally:
        default_storage.delete(filename)
        rmtree(tempdir)


def import_course_from_path(path, repo_id, user_id):
    """
    Import course from an OLX directory.

    Args:
        path (unicode): Path to extracted OLX tree
        repo_id (int): Primary key of repository course belongs to
        user_id (int): Primary key of Django user doing the import
    Returns:
        course (learningresources.Course)
    """
    bundle = XBundle(
        keep_urls=True, keep_studio_urls=True, preserve_url_name=True
    )
    bundle.import_from_directory(path)
    static_dir = join(path, 'static')
    course = import_course(bundle, repo_id, user_id, static_dir)
    return course


def import_course(bundle, repo_id, user_id, static_dir):
    """
    Import a course from an XBundle object.

    Args:
        bundle (xbundle.XBundle): Course as xbundle XML
        repo_id (int): Primary key of repository course belongs to
        user_id (int): Primary key of Django user doing the import
        static_dir (unicode): location of static files
    Returns:
        learningresources.models.Course
    """
    src = bundle.course
    course = create_course(
        org=src.attrib["org"],
        repo_id=repo_id,
        course_number=src.attrib["course"],
        run=src.attrib["semester"],
        user_id=user_id,
    )
    import_static_assets(course, static_dir)
    import_children(course, src, None, '')
    populate_xanalytics_fields.delay(course.id)
    # This triggers a bulk indexing of all LearningResource instances
    # for the course at once.
    index_resources(
        get_resources(repo_id).filter(course__id=course.id))
    return course


def import_children(course, element, parent, parent_dpath):
    """
    Create LearningResource instances for each element
    of an XML tree.

    Args:
        course (learningresources.models.Course): Course
        element (lxml.etree): XML element within xbundle
        parent (learningresources.models.LearningResource):
            Parent LearningResource
        parent_dpath (unicode): parent description path
    Returns:
        None
    """
    # pylint: disable=too-many-locals
    title = element.attrib.get("display_name", "MISSING")
    mpath = etree.ElementTree(element).getpath(element)
    dpath = join_description_paths(parent_dpath, title)
    resource = create_resource(
        course=course, parent=parent, resource_type=element.tag,
        title=title,
        content_xml=etree.tostring(element),
        mpath=mpath,
        url_name=element.attrib.get("url_name", None),
        dpath=dpath,
    )
    target = "/static/"
    if element.tag == "video":
        subname = get_video_sub(element)
        if subname != "":
            assets = StaticAsset.objects.filter(
                course__id=resource.course_id,
                asset=course_asset_basepath(course, subname),
            )
            for asset in assets:
                resource.static_assets.add(asset)
    else:
        # Recursively find all sub-elements, looking for anything which
        # refers to /static/. Then make the association between the
        # LearningResource and StaticAsset if the StaticAsset exists.
        # This is like doing soup.findAll("a") and checking for whether
        # "/static/" is in the href, which would work but also requires
        # more code to check for link, img, iframe, script, and others,
        # and within those, check for href or src existing.
        soup = BeautifulSoup(etree.tostring(element), 'lxml')
        for child in soup.findAll():
            for _, val in child.attrs.items():
                try:
                    if val.startswith(target):
                        path = val[len(target):]
                        try:
                            asset = StaticAsset.objects.get(
                                course__id=resource.course_id,
                                asset=course_asset_basepath(course, path),
                            )
                            resource.static_assets.add(asset)
                        except StaticAsset.DoesNotExist:
                            continue
                except AttributeError:
                    continue  # not a string

    for child in element.getchildren():
        if child.tag in DESCRIPTOR_TAGS:
            import_children(course, child, resource, dpath)
