from ovp_projects import models
from ovp_projects import helpers
from ovp_projects.decorators import hide_address, add_current_user_is_applied_representation
from ovp_projects.serializers.disponibility import DisponibilitySerializer, add_disponibility_representation
from ovp_projects.serializers.job import JobSerializer
from ovp_projects.serializers.work import WorkSerializer
from ovp_projects.serializers.role import VolunteerRoleSerializer
from ovp_projects.serializers.apply import ProjectAppliesSerializer

from ovp_core import models as core_models
from ovp_core.helpers import get_address_serializers
from ovp_core.serializers.cause import CauseSerializer, CauseAssociationSerializer, FullCauseSerializer
from ovp_core.serializers.skill import SkillSerializer, SkillAssociationSerializer

from ovp_uploads.serializers import UploadedImageSerializer

from ovp_organizations.serializers import OrganizationSearchSerializer
from ovp_organizations.models import Organization

from ovp_users.serializers import ShortUserPublicRetrieveSerializer, UserProjectRetrieveSerializer

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.compat import set_many
from rest_framework.utils import model_meta

""" Address serializers """
address_serializers = get_address_serializers()

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
  address = address_serializers[0]()
  disponibility = DisponibilitySerializer()
  roles = VolunteerRoleSerializer(many=True, required=False)
  causes = CauseAssociationSerializer(many=True, required=False)
  skills = SkillAssociationSerializer(many=True, required=False)

  class Meta:
    model = models.Project
    fields = ['id', 'image', 'name', 'slug', 'owner', 'details', 'description', 'highlighted', 'published', 'published_date', 'created_date', 'address', 'organization', 'disponibility', 'roles', 'max_applies', 'minimum_age', 'hidden_address', 'crowdfunding', 'public_project', 'causes', 'skills']
    read_only_fields = ['slug', 'highlighted', 'published', 'published_date', 'created_date']

  def create(self, validated_data):
    causes = validated_data.pop('causes', [])
    skills = validated_data.pop('skills', [])

    # Address
    address_data = validated_data.pop('address', {})
    address_sr = address_serializers[0](data=address_data)
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

    # Associate causes
    for cause in causes:
      c = core_models.Cause.objects.get(pk=cause['id'])
      project.causes.add(c)

    # Associate skills
    for skill in skills:
      s = core_models.Skill.objects.get(pk=skill['id'])
      project.skills.add(s)

    return project


  def update(self, instance, validated_data):
    causes = validated_data.pop('causes', [])
    skills = validated_data.pop('skills', [])
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
      address_sr = address_serializers[0](data=address_data)
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

    # Associate causes
    if causes:
      instance.causes.clear()
      for cause in causes:
        c = core_models.Cause.objects.get(pk=cause['id'])
        instance.causes.add(c)

    # Associate skills
    if skills:
      instance.skills.clear()
      for skill in skills:
        s = core_models.Skill.objects.get(pk=skill['id'])
        instance.skills.add(s)

    instance.save()

    return instance

  def get_validators(self):
    return super(ProjectCreateUpdateSerializer, self).get_validators() + [organization_validator]

  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectCreateUpdateSerializer, self).to_representation(instance)

class ProjectRetrieveSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = address_serializers[1]()
  organization = OrganizationSearchSerializer()
  disponibility = DisponibilitySerializer()
  roles = VolunteerRoleSerializer(many=True)
  owner = UserProjectRetrieveSerializer()
  applies = ProjectAppliesSerializer(many=True, source="active_apply_set")
  causes = FullCauseSerializer(many=True)
  skills = SkillSerializer(many=True)

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'details', 'created_date', 'organization', 'disponibility', 'roles', 'owner', 'minimum_age', 'applies', 'applied_count', 'max_applies', 'max_applies_from_roles', 'closed', 'closed_date', 'published', 'hidden_address', 'crowdfunding', 'public_project', 'causes', 'skills']

  @add_current_user_is_applied_representation
  @hide_address
  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectRetrieveSerializer, self).to_representation(instance)

class CompactOrganizationSerializer(serializers.ModelSerializer):
  address = address_serializers[2]()

  class Meta:
    model = Organization
    fields = ['name', 'address']

class ProjectOnOrganizationRetrieveSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = address_serializers[1]()
  disponibility = DisponibilitySerializer()
  causes = CauseSerializer(many=True)
  skills = SkillSerializer(many=True)
  owner = UserProjectRetrieveSerializer()
  organization = CompactOrganizationSerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'highlighted', 'published_date', 'address', 'details', 'created_date', 'disponibility', 'minimum_age', 'applied_count', 'max_applies', 'max_applies_from_roles', 'closed', 'closed_date', 'published', 'hidden_address', 'crowdfunding', 'public_project', 'causes', 'skills', 'owner', 'organization']

  @hide_address
  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectOnOrganizationRetrieveSerializer, self).to_representation(instance)


class ProjectSearchSerializer(serializers.ModelSerializer):
  image = UploadedImageSerializer()
  address = address_serializers[1]()
  organization = CompactOrganizationSerializer()
  owner = ShortUserPublicRetrieveSerializer()
  disponibility = DisponibilitySerializer()

  class Meta:
    model = models.Project
    fields = ['slug', 'image', 'name', 'description', 'disponibility', 'highlighted', 'published_date', 'address', 'organization', 'owner', 'applied_count', 'max_applies', 'hidden_address']

  @hide_address
  @add_disponibility_representation
  def to_representation(self, instance):
    return super(ProjectSearchSerializer, self).to_representation(instance)

