from rest_framework import serializers

from ovp_projects.models import VolunteerRole

class VolunteerRoleSerializer(serializers.ModelSerializer):
  class Meta:
    model = VolunteerRole
    fields = ['name', 'prerequisites', 'details', 'vacancies', 'applied_count']

class VolunteerRoleApplySerializer(serializers.ModelSerializer):
  class Meta:
    model = VolunteerRole
    fields = ['name', 'details']
