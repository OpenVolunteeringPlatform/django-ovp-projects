# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-27 21:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ovp_projects', '0040_auto_20170727_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteerrole',
            name='applied_count',
            field=models.IntegerField(default=0, verbose_name='Applied count'),
        ),
    ]
