from functools import wraps
from ovp_organizations.models import Organization
from ovp_projects import models

def hide_address(func):
  """ Used to decorate Serializer.to_representation method.
      It hides the address field if the Project has 'hidden_address' == True
      and the request user is neither owner or member of the organization """
  @wraps(func)
  def _impl(self, instance):
    # We pop address field to avoid AttributeError on default Serializer.to_representation
    if instance.hidden_address:
      for i, field in enumerate(self._readable_fields):
        if field.field_name == "address":
          address = self._readable_fields.pop(i)

      ret = func(self, instance)
      self._readable_fields.insert(i, address) # Put address back

      request = self.context["request"]

      # Check if user is organization member
      is_organization_member = False
      try:
        if instance.organization is not None:
          is_organization_member = (request.user in instance.organization.members.all())
      except Organization.DoesNotExist: # pragma: no cover
        pass


      # Add address representation
      if request.user == instance.owner or is_organization_member:
        ret["address"] = self.fields["address"].to_representation(instance.address)
      else:
        ret["address"] = None
    else:
      ret = func(self, instance)

    return ret
  return _impl


def add_current_user_is_applied_representation(func):
  """ Used to decorate Serializer.to_representation method.
      It sets the field "current_user_is_applied" if the user is applied to the project
  """
  @wraps(func)
  def _impl(self, instance):
    # We pop current_user_is_applied field to avoid AttributeError on default Serializer.to_representation
    ret = func(self, instance)

    user = self.context["request"].user
    applied = False
    if not user.is_anonymous():
      try:
        applied = models.Apply.objects.filter(user=user, project=instance).count() > 0
      except:
        pass

    ret["current_user_is_applied"] = applied

    return ret
  return _impl
