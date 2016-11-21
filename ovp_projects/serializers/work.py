from ovp_projects import models
from rest_framework import serializers

class WorkSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Work
    fields = ['weekly_hours', 'description', 'project']
    extra_kwargs = {'project': {'write_only': True}}
