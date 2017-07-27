# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-27 17:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ovp_projects', '0038_auto_20170627_0235'),
    ]

    operations = [
        migrations.AddField(
            model_name='apply',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ovp_projects.VolunteerRole', verbose_name='role'),
        ),
    ]
