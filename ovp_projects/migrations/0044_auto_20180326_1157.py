# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-03-26 11:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ovp_projects', '0043_project_handson_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteerrole',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Role name'),
        ),
    ]
