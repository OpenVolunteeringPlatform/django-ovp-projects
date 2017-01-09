from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_projects.models import JobDate


class JobDateInline(admin.TabularInline):
  model = JobDate


class JobDateAdmin(admin.ModelAdmin):
  list_display = ['id', 'start_date', 'end_date']
  raw_id_fields = ['job']


admin.site.register(JobDate, JobDateAdmin)


