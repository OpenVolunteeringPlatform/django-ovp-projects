# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-18 12:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ovp_projects', '0016_auto_20161116_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='availabilities',
        ),
        migrations.DeleteModel(
            name='Availability',
        ),
    ]