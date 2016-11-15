from ovp_projects import serializers
from ovp_projects import models

from ovp_users import models as users_models

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import response
from rest_framework import status

class ProjectResourceViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  """
  ProjectResourceViewSet resource endpoint
  """
  queryset = models.Project.objects.all()
  lookup_field = 'slug'
  lookup_value_regex = '[^/]+' # default is [^/.]+ - here we're allowing dots in the url slug field

  def create(self, request, *args, **kwargs):
    user = users_models.User.objects.all().first()
    request.data['owner'] = user.pk

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    headers = self.get_success_headers(serializer.data)
    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

  # We need to override get_permissions and get_serializer_class to work
  # with multiple serializers and permissions
  def get_permissions(self):
    request = self.get_serializer_context()['request']
    if self.action == 'create':
      self.permission_classes = (permissions.IsAuthenticated, )
    elif self.action in ['retrieve']:
      self.permission_classes = ()

    return super(ProjectResourceViewSet, self).get_permissions()

  def get_serializer_class(self):
    if self.action == 'create':
      return serializers.ProjectCreateSerializer
    return serializers.ProjectRetrieveSerializer
