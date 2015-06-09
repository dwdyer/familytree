# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_squashed_0007_auto_20150609_2101'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'documents')),
                ('title', models.CharField(max_length=100)),
                ('people', models.ManyToManyField(related_name='documents', to='people.Person')),
            ],
        ),
        migrations.AlterField(
            model_name='photograph',
            name='image',
            field=models.ImageField(upload_to=b'photos'),
        ),
    ]
