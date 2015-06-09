# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('people', '0004_auto_20150604_2157'),
    ]

    operations = [
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
        migrations.RemoveField(
            model_name='photograph',
            name='person',
        ),
        migrations.AddField(
            model_name='photograph',
            name='person',
            field=models.ManyToManyField(related_name='photos', to='people.Person'),
        ),
    ]
