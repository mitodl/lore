"""
Import OLX data into LORE.
"""

from __future__ import unicode_literals

from shutil import rmtree
import logging
from tempfile import mkdtemp
from os.path import join, exists
from os import remove, listdir

from xbundle import XBundle, DESCRIPTOR_TAGS
from lxml import etree
from archive import extract, ArchiveException

from learningresources.api import create_course, create_resource

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
    try:
        extract(path=filename, to_path=tempdir, method="safe")
    except ArchiveException as ex:
        log.debug("failed to extract: %s", ex)
        remove(filename)
        raise ValueError("Invalid OLX archive, unable to extract.")
    course_imported = False
    if "course.xml" in listdir(tempdir):
        import_course_from_path(tempdir, repo_id, user_id)
        course_imported = True
    else:
        for path in listdir(tempdir):
            if exists(join(tempdir, path, 'course.xml')):
                import_course_from_path(join(tempdir, path), repo_id, user_id)
                course_imported = True
    rmtree(tempdir)
    remove(filename)
    if course_imported is False:
        raise ValueError("Invalid OLX archive, no courses found.")


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
    return import_course(bundle, repo_id, user_id)


def import_course(bundle, repo_id, user_id):
    """
    Import a course from an XBundle object.

    Args:
        bundle (xbundle.XBundle): Course as xbundle XML
        repo_id (int): Primary key of repository course belongs to
        user_id (int): Primary key of Django user doing the import
    Returns:
        None
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
