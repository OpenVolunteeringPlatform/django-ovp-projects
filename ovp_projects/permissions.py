from rest_framework import permissions
from ovp_organizations.models import Organization


class OwnsOrIsOrganizationMember(permissions.BasePermission):
  def has_permission(self, request, view):
    organization_pk = request.data.get('organization', None)

    if not organization_pk:
      return True

    if not isinstance(organization_pk, int):
      return True # Should fail on validator

    try:
      organization = Organization.objects.get(pk=organization_pk, owner=request.user)
      return True
    except Organization.DoesNotExist:
      pass
    return False