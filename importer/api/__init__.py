"""
Import OLX data into LORE.
"""

# stdlib
from glob import glob
from shutil import rmtree
from tempfile import mkdtemp
from os.path import join
import tarfile
import zipfile

# PyPi

from xbundle import XBundle, DESCRIPTOR_TAGS
from lxml import etree

# MITODL
# commented out for now, until it's merged
# from lore.learningobjects.models import Course, LearningObject

def import_course_from_file(filename):
    """
    Import OLX from .zip or tar.gz.
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
    assert len(dirs) == 1
    import_course_from_path(dirs[0])
    rmtree(tempdir)

def import_course_from_path(path):
    """
    Import course from an OLX directory.
    """
    bundle = XBundle()
    bundle.import_from_directory(path)
    return import_course(bundle)


def import_course(bundle):
    """
    Import a course from an XBundle object.
    """
    course = Course()
    course.course_number = bundle.course.attrib.get("course", "MISSING")
    course.save()
    import_children(course, bundle.course, None)


def import_children(course, element, parent):
    """
    Create LearningObject instances for each element
    of an XML tree.
    """
    lox = LearningObject()
    lox.course = course
    lox.display_name = element.attrib.get("display_name", "MISSING")
    lox.tag = element.tag
    lox.xml = etree.tostring(element)
    if parent is not None:
        lox.parent = parent
    else:
        lox.display_name = "/".join([
            element.attrib.get(x, "MISSING")
            for x in ("org", "course", "semester")
        ])
    lox.save()
    for child in element.getchildren():
        if child.tag in DESCRIPTOR_TAGS:
            import_children(course, child, lox)

# Dummy placeholders.

class FakeModel(object):
    """
    Mock
    """
    def save(self):
        return True

class Course(FakeModel):
    """
    dummy
    """
    pass

class LearningObject(FakeModel):
    """
    dummy
    """
    pass

