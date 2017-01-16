from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_projects.models import Apply

from ovp_core.mixins import CountryFilterMixin


class ApplyAdmin(admin.ModelAdmin, CountryFilterMixin):
  fields = [
    ('id', 'project__name', 'status'),
    'user', 'project', 'project__organization__name',
    ('canceled', 'canceled_date', 'date'),
    'email'
    ]

  list_display = [
    'id', 'date', 'user__name', 'user__email', 'user__phone', 'project__name',
    'project__organization__name', 'project__address', 'status', 'canceled'
    ]

  list_filter = ['date', 'canceled',]

  list_editable = ['canceled',]

  search_fields = [
    'user__name', 'user__email', 'project__name',
    'project__organization__name'
    ]

  readonly_fields = [
    'id', 'project__name', 'user', 'project__organization__name',
    ]

  raw_id_fields = []

  def user__name(self, obj):
    if obj.user:
      return obj.user.name
    else:
      return _('None')

  user__name.short_description = _('Name')
  user__name.admin_order_field = 'user__name'

  def user__email(self, obj):
    if obj.user:
      return obj.user.email
    else:
      return _('None')
  user__email.short_description = _('E-mail')
  user__email.admin_order_field = 'user__email'

  def user__phone(self, obj):
    if obj.user:
      return obj.user.phone
    else:
      return _('None')
  user__phone.short_description = _('Phone')
  user__phone.admin_order_field = 'user__phone'

  def project__name(self, obj):
    if obj.project:
      return obj.project.name
    else:
      return _('None')
  project__name.short_description = _('Project')
  project__name.admin_order_field = 'project__name'

  def project__organization__name(self, obj):
    if obj.project and obj.project.organization:
      return obj.project.organization.name
    else:
      return _('None')
  project__organization__name.short_description = _('Organization')
  project__organization__name.project__organization__name = 'project__organization__name'

  def project__address(self, obj):
    if obj.project:
      return obj.project.address
    else:
      return _('None')
  project__address.short_description = _('Address')
  project__address.admin_order_field = 'project__address'

  def get_queryset(self, request):
    qs = super(ApplyAdmin, self).get_queryset(request)
    return self.filter_by_country(request, qs, 'project__address')

admin.site.register(Apply, ApplyAdmin)


