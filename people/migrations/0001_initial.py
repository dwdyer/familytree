# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
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
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('date_of_death', models.DateField(null=True, blank=True)),
                ('deceased', models.BooleanField()),
                ('father', models.ForeignKey(related_name='father_of', blank=True, to='people.Person', null=True)),
                ('mother', models.ForeignKey(related_name='mother_of', blank=True, to='people.Person', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Photograph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(null=True, upload_to=b'uploads', blank=True)),
                ('caption', models.TextField(blank=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('person', models.ForeignKey(to='people.Person')),
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
    ]
