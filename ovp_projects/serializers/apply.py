from ovp_projects import models
from ovp_projects.models.apply import apply_status_choices

from ovp_users.serializers import UserPublicRetrieveSerializer, UserApplyRetrieveSerializer

from rest_framework import serializers

class ApplyCreateSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)

  class Meta:
    model = models.Apply
    fields = ['username', 'email', 'phone', 'project', 'user']

class ApplyUpdateSerializer(serializers.ModelSerializer):
  status = serializers.ChoiceField(choices=apply_status_choices)

  class Meta:
    model = models.Apply
    fields = ['status']

class ApplyRetrieveSerializer(serializers.ModelSerializer):
  user = UserApplyRetrieveSerializer()
  status = serializers.SerializerMethodField()

  class Meta:
    model = models.Apply
    fields = ['id', 'email', 'date', 'canceled', 'canceled_date', 'status', 'user']

  def get_status(self, object):
    return object.get_status_display()


class ProjectAppliesSerializer(serializers.ModelSerializer):
  user = UserPublicRetrieveSerializer()

  class Meta:
    model = models.Apply
    fields = ['date', 'user']
