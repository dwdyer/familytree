# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_person_notes'),
    ]

    operations = [
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
        migrations.AlterField(
            model_name='person',
            name='father',
            field=models.ForeignKey(related_name='children_of_father', blank=True, to='people.Person', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='mother',
            field=models.ForeignKey(related_name='children_of_mother', blank=True, to='people.Person', null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='birth_location',
            field=models.ForeignKey(blank=True, to='people.Location', null=True),
        ),
    ]
