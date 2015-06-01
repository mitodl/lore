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
                ('run', models.TextField()),
                ('import_date', models.DateField(auto_now_add=True)),
                ('imported_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LearningResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.TextField()),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('content_xml', models.TextField()),
                ('materialized_path', models.TextField()),
                ('url_path', models.TextField()),
                ('copyright', models.TextField()),
                ('xa_nr_views', models.IntegerField(default=0)),
                ('xa_nr_attempts', models.IntegerField(default=0)),
                ('xa_avg_grade', models.FloatField(default=0)),
                ('xa_histogram_grade', models.FloatField(default=0)),
                ('course', models.ForeignKey(to='learningresources.Course')),
            ],
        ),
        migrations.CreateModel(
            name='LearningResourceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
                ('slug', models.CharField(unique=True, max_length=256)),
                ('description', models.TextField()),
                ('create_date', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='learningresource',
            name='learning_resource_type',
            field=models.ForeignKey(to='learningresources.LearningResourceType'),
        ),
        migrations.AddField(
            model_name='learningresource',
            name='parent',
            field=models.ForeignKey(blank=True, to='learningresources.LearningResource', null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='repository',
            field=models.ForeignKey(to='learningresources.Repository'),
        ),
    ]
