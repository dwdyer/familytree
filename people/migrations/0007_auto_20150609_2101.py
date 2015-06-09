# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_auto_20150609_2100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photograph',
            name='image',
            field=models.ImageField(upload_to=b'uploads'),
        ),
    ]
