from ovp_projects import models
from ovp_projects import helpers
from ovp_projects.serializers.disponibility import DisponibilitySerializer, add_disponibility_representation
from ovp_projects.serializers.job import JobSerializer
from ovp_projects.serializers.work import WorkSerializer

from ovp_core import models as core_models
from ovp_core import validators as core_validators
from ovp_core.serializers import GoogleAddressSerializer

from ovp_uploads.serializers import UploadedImageSerializer

from ovp_organizations.serializers import OrganizationSearchSerializer
from ovp_organizations.models import Organization

from rest_framework import serializers
from rest_framework import exceptions

""" Validators """
def organization_validator(data):
  settings = helpers.get_settings()
  allow_no_org = settings.get('CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION', False)

  if not allow_no_org:
    pk = data.get('organization', None)

    if not pk:
      raise exceptions.ValidationError({'organization': ['This field is required.']})


""" Serializers """
class ProjectCreateSerializer(serializers.ModelSerializer):
  address = GoogleAddressSerializer(
      validators=[core_validators.address_validate]
    )
  disponibility = DisponibilitySerializer()

  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address', 'organization', 'disponibility']
    read_only_fields = ['slug', 'highlighted', 'published', 'published_date', 'created_date']

  def create(self, validated_data):
    # Address
    address_data = validated_data.pop('address', {})
    address_sr = GoogleAddressSerializer(data=address_data)
    address = address_sr.create(address_data)
    validated_data['address'] = address

    # Disponibility
    disp = validated_data.pop('disponibility', {}) # we gotta pop before creating project

    # Create project
    project = models.Project.objects.create(**validated_data)

    # Disponibility
    if disp['type'] == 'work':
      work_data = disp['work']
      work_data['project'] = project
      work_sr = WorkSerializer(data=work_data)
      work = work_sr.create(work_data)

    if disp['type'] == 'job':
      job_data = disp['job']
      job_data['project'] = project
      job_sr = JobSerializer(data=job_data)
      job = job_sr.create(job_data)

    return project

  def get_validators(self):
    return super(ProjectCreateSerializer, self).get_validators() + [organization_validator]

  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectCreateSerializer, self).to_representation(instance)



class ProjectRetrieveSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = GoogleAddressSerializer()
  organization = OrganizationSearchSerializer()
  disponibility = DisponibilitySerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'details', 'created_date', 'organization', 'disponibility']

  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectRetrieveSerializer, self).to_representation(instance)


class ProjectSearchSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = GoogleAddressSerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address']



class ApplyCreateSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)

  class Meta:
    model = models.Apply
    fields = ['email', 'project']
