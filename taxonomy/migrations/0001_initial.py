# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

# pylint: skip-file

class Migration(migrations.Migration):

    dependencies = [
        ('learningresources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.TextField()),
                ('weight', models.IntegerField()),
                ('learning_resources', models.ManyToManyField(related_name='terms', to='learningresources.LearningResource')),
            ],
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('slug', models.CharField(unique=True, max_length=256)),
                ('description', models.TextField(help_text='Describe how content authors should use this vocabulary')),
                ('required', models.BooleanField()),
                ('vocabulary_type', models.CharField(default='m', help_text='Should terms be created in advance or on the fly?', max_length=1, choices=[('m', 'Managed'), ('f', 'Tag Style (on the fly)')])),
                ('weight', models.IntegerField()),
                ('learning_resource_types', models.ManyToManyField(help_text='Resource types this vocabulary applies to', related_name='vocabularies', to='learningresources.LearningResourceType')),
                ('repository', models.ForeignKey(to='learningresources.Repository', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='term',
            name='vocabulary',
            field=models.ForeignKey(to='taxonomy.Vocabulary', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterUniqueTogether(
            name='vocabulary',
            unique_together=set([('repository', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together=set([('vocabulary', 'label')]),
        ),
    ]
