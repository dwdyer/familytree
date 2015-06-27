# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_auto_20150619_2152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['surname', 'forename', 'middle_names', '-date_of_birth']},
        ),
        migrations.AddField(
            model_name='marriage',
            name='wedding_location',
            field=models.ForeignKey(related_name='weddings', blank=True, to='people.Location', null=True),
        ),
    ]
