"""
Learning resources data model
"""

from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """
    A course on edX platform (MITx or residential).
    """
    repository = models.ForeignKey('Repository')
    org = models.TextField()
    course_number = models.TextField()
    semester = models.TextField()
    import_date = models.DateField(auto_now_add=True)
    imported_by = models.ForeignKey(User)


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
    path_xml = models.TextField()
    mpath = models.TextField()
    url_path = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True)
    copyright = models.TextField()
    xa_nr_views = models.IntegerField(default=0)
    xa_nr_attempts = models.IntegerField(default=0)
    xa_avg_grade = models.FloatField(default=0)
    xa_histogram_grade = models.FloatField(default=0)


class LearningResourceType(models.Model):
    """
    Learning resource type:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    name = models.TextField()

    def __unicode__(self):
        return self.name


class Repository(models.Model):
    """
    A collection of learning resources
    that come from (usually tightly-related) courses.
    """
    name = models.TextField()
    description = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User)
