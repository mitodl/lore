"""
Learning resources data model
"""

from __future__ import unicode_literals

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible


class Course(models.Model):
    """
    A course on edX platform (MITx or residential).
    """
    repository = models.ForeignKey('Repository')
    org = models.TextField()
    course_number = models.TextField()
    run = models.TextField()
    import_date = models.DateField(auto_now_add=True)
    imported_by = models.ForeignKey(User)

    class Meta:
        # pylint: disable=invalid-name,missing-docstring,too-few-public-methods
        unique_together = ("repository", "org", "course_number", "run")


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
    materialized_path = models.TextField()
    url_path = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True)
    copyright = models.TextField()
    xa_nr_views = models.IntegerField(default=0)
    xa_nr_attempts = models.IntegerField(default=0)
    xa_avg_grade = models.FloatField(default=0)
    xa_histogram_grade = models.FloatField(default=0)

    class Meta:
        # pylint: disable=invalid-name,missing-docstring,too-few-public-methods
        unique_together = ("course", "uuid")


@python_2_unicode_compatible
class LearningResourceType(models.Model):
    """
    Learning resource type:
    chapter, sequential, vertical, problem, video, html, etc.
    """
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Repository(models.Model):
    """
    A collection of learning resources
    that come from (usually tightly-related) courses.
    """
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def has_resources(self):
        """Are any LearningResources uploaded for this repository?"""
        return LearningResource.objects.filter(
            course__repository__id=self.id).exists()

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Handle slugs."""
        slug = slugify(self.name)
        count = 1
        while Repository.objects.filter(slug=slug).exists():
            slug = "{0}{1}".format(slugify(self.name), count)
            count += 1
        self.slug = slug
        return super(Repository, self).save(*args, **kwargs)
