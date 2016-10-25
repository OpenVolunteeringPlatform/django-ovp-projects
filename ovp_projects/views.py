from ovp_projects import serializers
from ovp_projects import models

from ovp_users import models as users_models

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response

class ProjectResourceViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
  """
  ProjectResourceViewSet resource endpoint
  """
  queryset = models.Project.objects.all()

  def get_serializer_class(self):
    return serializers.ProjectCreateSerializer

  def create(self, request, *args, **kwargs):
    #request.data.owner = request.user.pk
    user = users_models.User.objects.all().first()
    request.data['owner'] = user.pk

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    model = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
