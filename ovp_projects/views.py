from ovp_projects import serializers
from ovp_projects import models
from ovp_projects import helpers

from ovp_users import models as users_models

from rest_framework import decorators
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


  @decorators.detail_route(['POST'])
  def apply(self, request, *args, **kwargs):
    data = request.data
    user = None

    project = self.get_object()
    data['project'] = project.id

    if request.user.is_authenticated():
      user = request.user
      data['email'] = user.email
      data['user'] = user.id

    apply_sr = serializers.ApplyCreateSerializer(data=data, context=self.get_serializer_context())
    apply_sr.is_valid(raise_exception=True)
    apply_sr.save()

    return response.Response({'detail': 'Successfully applied.'}, status=status.HTTP_200_OK)


  # We need to override get_permissions and get_serializer_class to work
  # with multiple serializers and permissions
  def get_permissions(self):
    request = self.get_serializer_context()['request']
    if self.action == 'create':
      self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'apply':
      settings = helpers.get_settings()
      if settings.get('UNAUTHENTICATED_APPLY', False):
        self.permission_classes = ()
      else:
        self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'retrieve':
      self.permission_classes = ()

    return super(ProjectResourceViewSet, self).get_permissions()

  def get_serializer_class(self):
    if self.action == 'create':
      return serializers.ProjectCreateSerializer
    if self.action == 'apply':
      return serializers.ApplyCreateSerializer

    return serializers.ProjectRetrieveSerializer
