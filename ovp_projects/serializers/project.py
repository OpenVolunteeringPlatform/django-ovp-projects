from ovp_projects import models
from ovp_projects import helpers
from ovp_projects.serializers.disponibility import DisponibilitySerializer, add_disponibility_representation
from ovp_projects.serializers.job import JobSerializer
from ovp_projects.serializers.work import WorkSerializer
from ovp_projects.serializers.role import VolunteerRoleSerializer

from ovp_core import models as core_models
from ovp_core import validators as core_validators
from ovp_core.serializers import GoogleAddressSerializer, GoogleAddressLatLngSerializer, GoogleAddressCityStateSerializer

from ovp_uploads.serializers import UploadedImageSerializer

from ovp_organizations.serializers import OrganizationSearchSerializer
from ovp_organizations.models import Organization

from ovp_users.serializers import UserPublicRetrieveSerializer, UserApplyRetrieveSerializer, UserProjectRetrieveSerializer

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.compat import set_many
from rest_framework.utils import model_meta

""" Validators """
def organization_validator(data):
  settings = helpers.get_settings()
  allow_no_org = settings.get('CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION', False)

  if not allow_no_org:
    pk = data.get('organization', None)

    if not pk:
      raise exceptions.ValidationError({'organization': ['This field is required.']})


""" Serializers """
class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
  address = GoogleAddressSerializer(
      validators=[core_validators.address_validate]
    )
  disponibility = DisponibilitySerializer()
  roles = VolunteerRoleSerializer(many=True, required=False)

  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address', 'organization', 'disponibility', 'roles']
    read_only_fields = ['slug', 'highlighted', 'published', 'published_date', 'created_date']

  def create(self, validated_data):
    # Address
    address_data = validated_data.pop('address', {})
    address_sr = GoogleAddressSerializer(data=address_data)
    address = address_sr.create(address_data)
    validated_data['address'] = address

    # We gotta pop some fields before creating project
    roles = validated_data.pop('roles', [])
    disp = validated_data.pop('disponibility', {})

    # Create project
    project = models.Project.objects.create(**validated_data)

    # Roles
    for role_data in roles:
      role_sr = VolunteerRoleSerializer(data=role_data)
      role = role_sr.create(role_data)
      project.roles.add(role)


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


  def update(self, instance, validated_data):
    address_data = validated_data.pop('address', None)
    roles = validated_data.pop('roles', None)
    disp = validated_data.pop('disponibility', None)

    # Iterate and save fields as drf default
    info = model_meta.get_field_info(instance)
    for attr, value in validated_data.items():
      # The following line is not covered because the current model does not implement
      # any many-to-many(except for roles, which is manually implemented)
      if attr in info.relations and info.relations[attr].to_many: # pragma: no cover
        set_many(instance, attr, value)
      else:
        setattr(instance, attr, value)

    # Save related resources
    if address_data:
      address_sr = GoogleAddressSerializer(data=address_data)
      address = address_sr.create(address_data)
      instance.address = address

    if roles:
      instance.roles.clear()
      for role_data in roles:
        role_sr = VolunteerRoleSerializer(data=role_data)
        role = role_sr.create(role_data)
        instance.roles.add(role)

    if disp:
      models.Work.objects.filter(project=instance).delete()
      models.Job.objects.filter(project=instance).delete()

      if disp['type'] == 'work':
        work_data = disp['work']
        work_data['project'] = instance
        work_sr = WorkSerializer(data=work_data)
        work = work_sr.create(work_data)

      if disp['type'] == 'job':
        job_data = disp['job']
        job_data['project'] = instance
        job_sr = JobSerializer(data=job_data)
        job = job_sr.create(job_data)

    instance.save()

    return instance

  def get_validators(self):
    return super(ProjectCreateUpdateSerializer, self).get_validators() + [organization_validator]

  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectCreateUpdateSerializer, self).to_representation(instance)


class ApplyCreateSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)

  class Meta:
    model = models.Apply
    fields = ['email', 'project', 'user']


class ApplyRetrieveSerializer(serializers.ModelSerializer):
  user = UserApplyRetrieveSerializer()

  class Meta:
    model = models.Apply
    fields = ['email', 'date', 'canceled', 'canceled_date', 'status', 'user']


class ProjectAppliesSerializer(serializers.ModelSerializer):
  user = UserPublicRetrieveSerializer()

  class Meta:
    model = models.Apply
    fields = ['date', 'user']


class ProjectRetrieveSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = GoogleAddressLatLngSerializer()
  organization = OrganizationSearchSerializer()
  disponibility = DisponibilitySerializer()
  roles = VolunteerRoleSerializer(many=True)
  owner = UserProjectRetrieveSerializer()
  applies = ProjectAppliesSerializer(many=True, source="active_apply_set")

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'details', 'created_date', 'organization', 'disponibility', 'roles', 'owner', 'applies', 'applied_count', 'max_applies_from_roles', 'closed', 'closed_date', 'published']

  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectRetrieveSerializer, self).to_representation(instance)


class CompactOrganizationSerializer(serializers.ModelSerializer):
  address = GoogleAddressCityStateSerializer()

  class Meta:
    model = Organization
    fields = ['name', 'address']


class ProjectSearchSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = GoogleAddressSerializer()
  organization = CompactOrganizationSerializer()
  owner = UserPublicRetrieveSerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'organization', 'owner']
