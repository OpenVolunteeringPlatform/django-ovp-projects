from ovp_projects import models

from rest_framework import serializers

class ProjectCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Project
    fields = ['id', 'name', 'slug', 'owner', 'highlighted', 'published', 'published_date', 'created_date']
    read_only_fields = ['highlighted', 'published', 'published_date', 'created_date']

class ProjectSearchSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Project
    fields = ['id', 'name', 'slug', 'highlighted', 'published', 'published_date', 'created_date']
    read_only_fields = ['highlighted', 'published', 'published_date', 'created_date']
