from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_projects.models import Project


class ProjectAdmin(admin.ModelAdmin):
  fields = [
    ('id', 'highlighted'), ('name', 'slug'),
    ('organization', 'owner'),

    ('applied_count', 'max_applies_from_roles'),

    ('published', 'closed', 'deleted'),
    ('published_date', 'closed_date', 'deleted_date'),

    'address',
    'image',

    ('created_date', 'modified_date'),

    'description', 'details',
    'skills', 'causes', 'roles',
    ]

  list_display = [
    'id', 'created_date', 'name', 'organization__name', 'applied_count', # fix: CIDADE, PONTUAL OU RECORRENTE
    'highlighted', 'published', 'closed', 'deleted', #fix: EMAIL STATUS
    ]

  list_filter = [
    'created_date', # fix: PONTUAL OU RECORRENTE
    'highlighted', 'published', 'closed', 'deleted'
  ]

  list_editable = [
    'highlighted', 'published', 'closed'
  ]

  search_fields = [
    'name', 'organization__name'
  ]

  readonly_fields = [
    'id', 'created_date', 'modified_date', 'published_date', 'closed_date', 'deleted_date'
  ]

  raw_id_fields = []


  def organization__name(self, obj):
    return obj.organization.name
  organization__name.short_description = _('Organization')
  organization__name.admin_order_field = 'organization__name'


admin.site.register(Project, ProjectAdmin)


