from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from ovp_projects.serializers import project as serializers
from ovp_projects import models
from ovp_projects import helpers
from ovp_projects.permissions import ProjectCreateOwnsOrIsOrganizationMember, OwnsOrIsOrganizationMember

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
    request.data['owner'] = request.user.pk

    serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
    serializer.is_valid(raise_exception=True)
    serializer.save()

    headers = self.get_success_headers(serializer.data)
    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


  def partial_update(self, request, *args, **kwargs):
    """ We do not include the mixin as we want only PATCH and no PUT """
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=True, context=self.get_serializer_context())
    serializer.is_valid(raise_exception=True)
    serializer.save()

    if getattr(instance, '_prefetched_objects_cache', None): #pragma: no cover
      instance = self.get_object()
      serializer = self.get_serializer(instance)

    return response.Response(serializer.data)

  @decorators.detail_route(['POST'])
  def close(self, request, *args, **kwargs):
    project = self.get_object()
    project.closed = True
    project.save()
    serializer = self.get_serializer_class()(project, context=self.get_serializer_context())
    return response.Response(serializer.data)

  @decorators.list_route(['GET'])
  def manageable(self, request, *args, **kwargs):
    projects = models.Project.objects.filter(Q(owner=request.user) | Q(organization__owner=request.user) | Q(organization__members=request.user))

    serializer = self.get_serializer_class()(projects, many=True, context=self.get_serializer_context())
    return response.Response(serializer.data)

  @decorators.detail_route(['POST'])
  def apply(self, request, *args, **kwargs):
    data = request.data
    data.pop('user', None)

    project = self.get_object()
    data['project'] = project.id

    if request.user.is_authenticated():
      user = request.user
      data['email'] = user.email
      data['user'] = user.id

    try:
      existing_apply = models.Apply.objects.get(project=project, email=data['email'], canceled=True)
      existing_apply.canceled = False
      existing_apply.save()
    except ObjectDoesNotExist:
      apply_sr = self.get_serializer_class()(data=data, context=self.get_serializer_context())
      apply_sr.is_valid(raise_exception=True)
      apply_sr.save()

    return response.Response({'detail': 'Successfully applied.'}, status=status.HTTP_200_OK)

  @decorators.detail_route(['POST'])
  def unapply(self, request, *args, **kwargs):
    project = self.get_object()
    user = request.user

    try:
      existing_apply = models.Apply.objects.get(project=project, email=user.email, canceled=False)
      existing_apply.canceled = True
      existing_apply.save()
    except ObjectDoesNotExist:
      return response.Response({'detail': 'This is user is not applied to this project.'}, status=status.HTTP_400_BAD_REQUEST)

    return response.Response({'detail': 'Successfully unapplied.'}, status=status.HTTP_200_OK)

  @decorators.detail_route(['GET'])
  def applies(self, request, *arg, **kwargs):
    project = self.get_object()
    applies = models.Apply.objects.filter(project=project)

    serializer = self.get_serializer_class()(applies, many=True, context=self.get_serializer_context())

    return response.Response(serializer.data)


  # We need to override get_permissions and get_serializer_class to work
  # with multiple serializers and permissions
  def get_permissions(self):
    request = self.get_serializer_context()['request']
    if self.action == 'create':
      if helpers.get_settings().get('CAN_CREATE_PROJECTS_IN_ANY_ORGANIZATION', False):
        self.permission_classes = (permissions.IsAuthenticated, )
      else:
        self.permission_classes = (permissions.IsAuthenticated, ProjectCreateOwnsOrIsOrganizationMember)

    if self.action in ['applies', 'partial_update']:
      self.permission_classes = (permissions.IsAuthenticated, OwnsOrIsOrganizationMember, )

    if self.action == 'unapply':
      self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'apply':
      if helpers.get_settings().get('UNAUTHENTICATED_APPLY', False):
        self.permission_classes = ()
      else:
        self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'retrieve':
      self.permission_classes = ()

    if self.action == 'manageable':
      self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'close':
      self.permission_classes = (permissions.IsAuthenticated, OwnsOrIsOrganizationMember, )

    return super(ProjectResourceViewSet, self).get_permissions()

  def get_serializer_class(self):
    if self.action in ['create', 'partial_update']:
      return serializers.ProjectCreateUpdateSerializer
    if self.action in ['apply', 'unapply']:
      return serializers.ApplyCreateSerializer
    if self.action == 'applies':
      return serializers.ApplyRetrieveSerializer
    if self.action == 'manageable':
      return serializers.ProjectRetrieveSerializer
    if self.action == 'close':
      return serializers.ProjectRetrieveSerializer

    return serializers.ProjectRetrieveSerializer
