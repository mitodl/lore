# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

# pylint: skip-file


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('repository', models.ForeignKey(
                    to='learningobjects.Repository')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('required', models.BooleanField()),
                ('vocabulary_type', models.CharField(max_length=1, choices=(
                    ("m", "managed"),
                    ("f", "free tagging")
                ))),
                ('weight', models.IntegerField()),
                ('learning_object_types',
                 models.ManyToManyField("learningobjects.LearningObjectType",
                                        related_name="vocabularies"))
            ]
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('vocabulary', models.ForeignKey(to="taxonomy.Vocabulary")),
                ('label', models.TextField()),
                ('weight', models.IntegerField()),
                ('learning_objects',
                 models.ManyToManyField("learningobjects.LearningObject",
                                        related_name="terms"))
            ]
        ),
    ]
