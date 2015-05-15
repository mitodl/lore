"""
Import OLX data into LORE.
"""

from glob import glob
from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp
from os.path import join
import tarfile
import zipfile

from xbundle import XBundle, DESCRIPTOR_TAGS
from lxml import etree

from learningobjects.api import create_course


def import_course_from_file(filename, user_id):
    """
    Import OLX from .zip or tar.gz.

    Args:
        filename (unicode): Path to archive file (zip or .tar.gz)
    Raises:
        ValueError: Unable to find single path inside archive file.
    Returns: None
    """
    tempdir = mkdtemp()
    if filename.endswith(".tar.gz"):
        course = tarfile.open(filename, "r")
    elif filename.endswith(".zip"):
        course = zipfile.ZipFile(filename, "r")
    else:
        raise ValueError("Unexpected file type (want tarball or zip).")
    course.extractall(tempdir)
    dirs = glob(join(tempdir, "*"))
    if len(dirs) != 1:
        raise ValueError("Unable to get course directory.")
    import_course_from_path(dirs[0], user_id)
    rmtree(tempdir)


def import_course_from_path(path, user_id):
    """
    Import course from an OLX directory.
    """
    bundle = XBundle()
    bundle.import_from_directory(path)
    return import_course(bundle, user_id)


def import_course(bundle, user_id):
    """
    Import a course from an XBundle object.
    """
    src = bundle.course
    course = create_course(
        org=src.attrib["org"],
        course_number=src.attrib["course"],
        semester=src.attrib["semester"],
        user_id=user_id,
    )

def import_children(course, element, parent):
    """
    Create LearningObject instances for each element
    of an XML tree.
    """

    # TODO: make a function in learningobjects.api instead
    # of doing it here, then consume it here.
    #lox.course = course
    #lox.display_name = element.attrib.get("display_name", "MISSING")
    #lox.tag = element.tag
    #lox.xml = etree.tostring(element)
    #if parent is not None:
    #    lox.parent = parent
    #else:
    #    lox.display_name = "/".join([
    ##        element.attrib.get(x, "MISSING")
    #        for x in ("org", "course", "semester")
    #    ])
    #lox.save()
    #for child in element.getchildren():
    #    if child.tag in DESCRIPTOR_TAGS:
    #        import_children(course, child, lox)
