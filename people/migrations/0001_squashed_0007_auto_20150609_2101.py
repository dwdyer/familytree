# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import taggit.managers


class Migration(migrations.Migration):

    replaces = [('people', '0001_initial'), ('people', '0002_auto_20150601_0036'), ('people', '0003_person_notes'), ('people', '0004_auto_20150604_2157'), ('people', '0005_auto_20150609_2052'), ('people', '0006_auto_20150609_2100'), ('people', '0007_auto_20150609_2101')]

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marriage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wedding_date', models.DateField()),
                ('divorce_date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forename', models.CharField(max_length=20)),
                ('middle_names', models.CharField(max_length=50, blank=True)),
                ('surname', models.CharField(max_length=30)),
                ('maiden_name', models.CharField(max_length=30, blank=True)),
                ('gender', models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('date_of_death', models.DateField(null=True, blank=True)),
                ('deceased', models.BooleanField()),
                ('father', models.ForeignKey(related_name='children_of_father', blank=True, to='people.Person', null=True)),
                ('mother', models.ForeignKey(related_name='children_of_mother', blank=True, to='people.Person', null=True)),
                ('notes', tinymce.models.HTMLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Photograph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(null=True, upload_to='uploads', blank=True)),
                ('caption', models.TextField(blank=True)),
                ('date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='marriage',
            name='husband',
            field=models.ForeignKey(related_name='wife_of', to='people.Person'),
        ),
        migrations.AddField(
            model_name='marriage',
            name='wife',
            field=models.ForeignKey(related_name='husband_of', to='people.Person'),
        ),
        migrations.AlterField(
            model_name='marriage',
            name='wedding_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('country_code', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('county_state_province', models.CharField(max_length=30)),
                ('country', models.ForeignKey(to='people.Country')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='birth_location',
            field=models.ForeignKey(blank=True, to='people.Location', null=True),
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name_plural': 'countries'},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['country', 'county_state_province', 'name']},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['surname', '-date_of_birth']},
        ),
        migrations.AddField(
            model_name='person',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='person',
            name='deceased',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='photograph',
            name='people',
            field=models.ManyToManyField(related_name='photos', to='people.Person'),
        ),
        migrations.AlterField(
            model_name='photograph',
            name='image',
            field=models.ImageField(upload_to='uploads'),
        ),
    ]
