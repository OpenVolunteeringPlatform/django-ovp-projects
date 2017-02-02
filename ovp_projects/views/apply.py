from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import Http404

from ovp_projects.serializers import apply as serializers
from ovp_projects import models
from ovp_projects import helpers
from ovp_projects.permissions import ProjectApplyPermission

from rest_framework import decorators
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import response
from rest_framework import status

class ApplyResourceViewSet(viewsets.GenericViewSet):
  """
  ApplyResourceViewSet resource endpoint
  """

  ##################
  # ViewSet routes #
  ##################
  def list(self, request, *arg, **kwargs):
    applies = self.get_queryset(**kwargs)
    serializer = self.get_serializer_class()(applies, many=True, context=self.get_serializer_context())

    return response.Response(serializer.data)

  def partial_update(self, request, *args, **kwargs):
    instance = self.get_queryset(**kwargs).get(pk=kwargs['pk'])
    serializer = self.get_serializer(instance, data=request.data, partial=True, context=self.get_serializer_context())
    serializer.is_valid(raise_exception=True)
    serializer.save()

    if getattr(instance, '_prefetched_objects_cache', None): #pragma: no cover
      instance = self.get_object()
      serializer = self.get_serializer(instance)

    return response.Response(serializer.data)

  @decorators.list_route(['POST'])
  def apply(self, request, *args, **kwargs):
    data = request.data
    data.pop('user', None)

    project = self.get_project_object(**kwargs)
    data['project'] = project.id

    if request.user.is_authenticated():
      user = request.user
      data['username'] = user.name
      data['email'] = user.email
      data['phone'] = user.phone
      data['user'] = user.id

    try:
      existing_apply = self.get_queryset(**kwargs).get(email=data['email'], canceled=True)
      existing_apply.canceled = False
      existing_apply.save()
    except ObjectDoesNotExist:
      apply_sr = self.get_serializer_class()(data=data, context=self.get_serializer_context())
      apply_sr.is_valid(raise_exception=True)
      apply_sr.save()

    return response.Response({'detail': 'Successfully applied.'}, status=status.HTTP_200_OK)

  @decorators.list_route(['POST'])
  def unapply(self, request, *args, **kwargs):
    project = self.get_project_object(**kwargs)
    user = request.user

    try:
      existing_apply = self.get_queryset(**kwargs).get(email=user.email, canceled=False)
      existing_apply.canceled = True
      existing_apply.save()
    except ObjectDoesNotExist:
      return response.Response({'detail': 'This is user is not applied to this project.'}, status=status.HTTP_400_BAD_REQUEST)

    return response.Response({'detail': 'Successfully unapplied.'}, status=status.HTTP_200_OK)


  ###################
  # ViewSet methods #
  ###################
  def get_queryset(self, *args, **kwargs):
    project = self.get_project_object(**kwargs)
    return models.Apply.objects.filter(project=project)

  def get_serializer_class(self):
    if self.action == 'list':
      return serializers.ApplyRetrieveSerializer

    if self.action == 'partial_update':
      return serializers.ApplyUpdateSerializer

    if self.action in ['apply', 'unapply']:
      return serializers.ApplyCreateSerializer

  def get_permissions(self):
    request = self.get_serializer_context()['request']

    if self.action in ['list', 'partial_update']:
      self.permission_classes = (permissions.IsAuthenticated, ProjectApplyPermission)

    if self.action == 'apply':
      if helpers.get_settings().get('UNAUTHENTICATED_APPLY', False):
        self.permission_classes = ()
      else:
        self.permission_classes = (permissions.IsAuthenticated, )

    if self.action == 'unapply':
      self.permission_classes = (permissions.IsAuthenticated, )


    return super(ApplyResourceViewSet, self).get_permissions()

  def get_project_object(self, *args, **kwargs):
    slug=kwargs.get('project_slug')

    return get_object_or_404(models.Project, slug=slug)
