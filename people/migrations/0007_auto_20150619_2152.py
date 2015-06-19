# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_auto_20150619_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marriage',
            name='divorce_date',
        ),
        migrations.AddField(
            model_name='marriage',
            name='divorced',
            field=models.BooleanField(default=False),
        ),
    ]
