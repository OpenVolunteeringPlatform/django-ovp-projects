from ovp_projects import models

from ovp_users.serializers import UserPublicRetrieveSerializer, UserApplyRetrieveSerializer

from rest_framework import serializers

class ApplyCreateSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)

  class Meta:
    model = models.Apply
    fields = ['username', 'email', 'phone', 'project', 'user']


class ApplyRetrieveSerializer(serializers.ModelSerializer):
  user = UserApplyRetrieveSerializer()

  class Meta:
    model = models.Apply
    fields = ['id', 'email', 'date', 'canceled', 'canceled_date', 'status', 'user']


class ProjectAppliesSerializer(serializers.ModelSerializer):
  user = UserPublicRetrieveSerializer()

  class Meta:
    model = models.Apply
    fields = ['date', 'user']
