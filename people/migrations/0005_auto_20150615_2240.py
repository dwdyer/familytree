# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import people.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_auto_20150613_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='date_of_birth',
            field=people.fields.UncertainDateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='date_of_death',
            field=people.fields.UncertainDateField(null=True, blank=True),
        ),
    ]
