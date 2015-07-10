# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0008_auto_20150627_1538'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='marriage',
            options={'ordering': ['husband__surname', 'husband__forename', 'husband__middle_names', 'wedding_date']},
        ),
        migrations.AddField(
            model_name='person',
            name='blood_relative',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='father',
            field=models.ForeignKey(related_name='children_of_father', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='people.Person', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='mother',
            field=models.ForeignKey(related_name='children_of_mother', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='people.Person', null=True),
        ),
    ]
