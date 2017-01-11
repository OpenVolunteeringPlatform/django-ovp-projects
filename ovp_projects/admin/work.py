from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_projects.models import Work


class WorkAdmin(admin.ModelAdmin):
  fields = [
  	('id', 'project'),
  	'weekly_hours',
  	'description',
  	'can_be_done_remotely',
  ]

  list_display = [
  	'id', 'project', 'weekly_hours', 'can_be_done_remotely'
  ]

  list_filter = []

  list_editable = ['can_be_done_remotely']

  search_fields = ['project__name', 'project__organization__name']

  readonly_fields = ['id']

  raw_id_fields = []


class WorkInline(admin.TabularInline):
  model = Work


admin.site.register(Work, WorkAdmin)


