# Generated by Django 2.2.24 on 2021-09-10 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='blood_relative',
        ),
    ]
