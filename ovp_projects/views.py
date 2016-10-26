from ovp_projects import serializers
from ovp_projects import models

from ovp_users import models as users_models

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status

class ProjectResourceViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  """
  ProjectResourceViewSet resource endpoint
  """
  queryset = models.Project.objects.all()
  lookup_field = 'slug'
  lookup_value_regex = '[^/]+' # default is [^/.]+ - here we're allowing dots in the url slug field

  def get_serializer_class(self):
    if self.action == "create":
      return serializers.ProjectCreateSerializer

    return serializers.ProjectSearchSerializer

  def create(self, request, *args, **kwargs):
    request.data['owner'] = request.user.id

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    headers = self.get_success_headers(serializer.data)
    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
