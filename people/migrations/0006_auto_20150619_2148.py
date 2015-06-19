# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import people.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_auto_20150615_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marriage',
            name='divorce_date',
            field=people.fields.UncertainDateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='marriage',
            name='wedding_date',
            field=people.fields.UncertainDateField(null=True, blank=True),
        ),
    ]
