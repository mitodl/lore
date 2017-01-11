# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# pylint: skip-file

def move_content_xml(apps, schema_editor):
    LearningResource = apps.get_model("learningresources", "LearningResource")
    LearningResourceContentXml = apps.get_model("learningresources", "LearningResourceContentXml")

    for resource in LearningResource.objects.iterator():
        obj = LearningResourceContentXml.objects.create(content_xml=resource.content_xml)
        # Hack to not emit post_save signal which will trigger reindex
        LearningResource.objects.filter(id=resource.id).update(
            content_xml=None,
            content_xml_model_id=obj.id
        )


def revert_content_xml(apps, schema_editor):
    LearningResource = apps.get_model("learningresources", "LearningResource")
    LearningResourceContentXml = apps.get_model("learningresources", "LearningResourceContentXml")

    for resource in LearningResource.objects.iterator():
        resource.content_xml = resource.content_xml_model.content_xml
        LearningResource.objects.filter(id=resource.id).update(content_xml=resource.content_xml_model.content_xml)


class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0019_add_content_xml_table'),
    ]

    operations = [
        migrations.RunPython(move_content_xml, revert_content_xml),
    ]
