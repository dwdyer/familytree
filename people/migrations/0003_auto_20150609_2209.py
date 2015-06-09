# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_auto_20150609_2128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photograph',
            options={'ordering': ['date']},
        ),
    ]
