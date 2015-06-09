# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_auto_20150609_2052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photograph',
            old_name='person',
            new_name='people',
        ),
    ]
