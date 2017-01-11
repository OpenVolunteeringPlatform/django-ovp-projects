from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_projects.models import Job, JobDate

from .jobdate import JobDateAdmin, JobDateInline


class JobAdmin(admin.ModelAdmin):
  #exclude=['dates']
  list_display = ['id', 'project', 'start_date', 'end_date']
  search_fields = ['id', 'project__name', 'project__nonprofit__name']

  inlines = (
    JobDateInline,
  )


class JobInline(admin.TabularInline):
  model = Job


admin.site.register(Job, JobAdmin)


