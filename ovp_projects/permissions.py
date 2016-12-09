from rest_framework import permissions
from ovp_organizations.models import Organization


class ProjectCreateOwnsOrIsOrganizationMember(permissions.BasePermission):
  def has_permission(self, request, view):
    organization_pk = request.data.get('organization', None)

    if not organization_pk:
      return True

    if not isinstance(organization_pk, int):
      return True # Should fail on validator

    try:
      organization = Organization.objects.get(pk=organization_pk)
      if organization.owner == request.user or request.user in organization.members.all():
        return True
    except Organization.DoesNotExist: #pragma: no cover
      pass
    return False


class OwnsOrIsOrganizationMember(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    if request.user.is_authenticated:
      if obj.owner == request.user:
        return True
      if obj.organization:
        if request.user in obj.organization.members.all():
          return True
    return False
