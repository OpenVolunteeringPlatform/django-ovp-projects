from ovp_projects import models

from ovp_core import models as core_models
from ovp_core.serializers import GoogleAddressSerializer

from rest_framework import serializers

class ProjectCreateSerializer(serializers.ModelSerializer):
  address = GoogleAddressSerializer()

  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address']
    read_only_fields = ['highlighted', 'published', 'published_date', 'created_date']

  def create(self, validated_data):
    address_data = validated_data.pop('address')
    address_sr = GoogleAddressSerializer(data=address_data)
    address_sr.is_valid(raise_exception=True)
    address = address_sr.create(address_data)

    validated_data['address'] = address
    project = models.Project.objects.create(**validated_data)
    return project

class ProjectSearchSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address']
    read_only_fields = ['highlighted', 'published', 'published_date', 'created_date']
