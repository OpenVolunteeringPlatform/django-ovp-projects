from ovp_projects import models

from ovp_core import models as core_models
from ovp_core.serializers import GoogleAddressSerializer

from ovp_uploads.serializers import UploadedImageSerializer

from ovp_organizations.serializers import OrganizationSearchSerializer

from rest_framework import serializers

class ProjectCreateSerializer(serializers.ModelSerializer):
  address = GoogleAddressSerializer()

  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address', 'organization']
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
  image = UploadedImageSerializer()
  address = GoogleAddressSerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address']


class ProjectRetrieveSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = GoogleAddressSerializer()
  organization = OrganizationSearchSerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'details', 'created_date', 'organization']


class ApplyCreateSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)

  class Meta:
    model = models.Apply
    fields = ['email', 'project']
