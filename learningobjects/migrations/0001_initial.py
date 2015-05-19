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
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org', models.TextField()),
                ('course_number', models.TextField()),
                ('semester', models.TextField()),
                ('import_date', models.DateField(auto_now_add=True)),
                ('imported_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LearningObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.TextField()),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('content_xml', models.TextField()),
                ('path_xml', models.TextField()),
                ('mpath', models.TextField()),
                ('url_path', models.TextField()),
                ('copyright', models.TextField()),
                ('xa_nr_views', models.IntegerField(default=0)),
                ('xa_nr_attempts', models.IntegerField(default=0)),
                ('xa_avg_grade', models.FloatField(default=0)),
                ('xa_histogram_grade', models.FloatField(default=0)),
                ('course', models.ForeignKey(to='learningobjects.Course')),
            ],
        ),
        migrations.CreateModel(
            name='LearningObjectType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('create_date', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='learningobject',
            name='learning_object_type',
            field=models.ForeignKey(to='learningobjects.LearningObjectType'),
        ),
        migrations.AddField(
            model_name='learningobject',
            name='parent',
            field=models.ForeignKey(blank=True, to='learningobjects.LearningObject', null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='repository',
            field=models.ForeignKey(to='learningobjects.Repository'),
        ),
    ]
