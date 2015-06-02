# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_auto_20150601_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='notes',
            field=tinymce.models.HTMLField(blank=True),
        ),
    ]
