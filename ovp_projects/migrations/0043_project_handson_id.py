# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-03-26 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ovp_projects', '0042_auto_20180115_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='handson_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='HandsOn id'),
        ),
    ]