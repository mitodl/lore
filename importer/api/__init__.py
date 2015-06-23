"""
Import OLX data into LORE.
"""

from __future__ import unicode_literals

from shutil import rmtree
import logging
from tempfile import mkdtemp
from os.path import join, exists, isdir
from os import listdir, walk, sep

from archive import Archive, ArchiveException
from django.core.files import File
from django.core.files.storage import default_storage
from lxml import etree
from xbundle import XBundle, DESCRIPTOR_TAGS

from learningresources.api import (
    create_course,
    create_resource,
    create_static_asset
)

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
    bundle = XBundle()
    bundle.import_from_directory(path)
    course = import_course(bundle, repo_id, user_id)
    static_dir = join(path, 'static')
    if isdir(static_dir):
        import_static_assets(static_dir, course)
    return course


def import_course(bundle, repo_id, user_id):
    """
    Import a course from an XBundle object.

    Args:
        bundle (xbundle.XBundle): Course as xbundle XML
        repo_id (int): Primary key of repository course belongs to
        user_id (int): Primary key of Django user doing the import
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
    import_children(course, src, None)
    return course


def import_children(course, element, parent):
    """
    Create LearningResource instances for each element
    of an XML tree.

    Args:
        course (learningresources.Course): Course
        element (lxml.etree): XML element within xbundle
        parent (learningresources.LearningResource): Parent LearningResource
    Returns:
        None
    """
    mpath = etree.ElementTree(element).getpath(element)
    resource = create_resource(
        course=course, parent=parent, resource_type=element.tag,
        title=element.attrib.get("display_name", "MISSING"),
        content_xml=etree.tostring(element),
        mpath=mpath,
    )
    for child in element.getchildren():
        if child.tag in DESCRIPTOR_TAGS:
            import_children(course, child, resource)


def import_static_assets(path, course):
    """
    Upload all assets and create model records of them for a given
    course and path.

    Args:
        path (unicode): course specific path to extracted OLX tree.
        course (learningresources.models.Course): Course to add assets to.
    Returns:
        None
    """
    for root, _, files in walk(path):
        for name in files:
            with open(join(root, name), 'r') as open_file:
                django_file = File(open_file)
                # Remove base path from file name
                django_file.name = join(root, name).replace(path + sep, '', 1)
                create_static_asset(course.id, django_file)


def parse_static(learning_resource):
    """
    Parse static assets from LearningResource XML.

    learning_resource_types can be 'html', 'problem', or 'video'.

    Args:
        learning_resource (LearningResource):

    Returns:
        List of green, slimy things
    """
    tree = etree.fromstring(learning_resource.content_xml)
    # expecting only one sub attribute in video LR.
    if learning_resource.learning_resource_type.name == "video":
        sub = tree.xpath("/video/@sub")
        # convert sub into filename
        if len(sub) > 0:
            filename = _subs_filename(sub)
            log.info('subtitle filename is %s'.format(filename))

    elif learning_resource.learning_resource_type.name == "html":
        tree.xpath("/div/")

    elif learning_resource.learning_resource_type.name == "problem":
        pass


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
    if lang == 'en':
        return u'subs_{0}.srt.sjson'.format(subs_id)
    else:
        return u'{0}_subs_{1}.srt.sjson'.format(lang, subs_id)


def _parse_relative_asset_path(path):
    """
    Extract path to static asset file from relative edX path

    Static assets whose location are relative to edX datastore such as
    ``/c4x/edX/DemoX/asset/images_logic_gate_image.png`` can be
    converted to a local path by extracting the portion of the path
    after ``asset/``.

    Args:
        path (str):

    Returns:
        Path to asset relative to ``static`` directory
    """
    return path.split('/asset/')[1]
