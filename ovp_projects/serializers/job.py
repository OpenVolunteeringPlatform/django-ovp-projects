from ovp_projects import models
from rest_framework import serializers

"""
Validators
"""
def dates_validator(data):
  dates = data.get('dates', None)

  if len(dates) < 1:
    raise serializers.ValidationError({"dates": ["Must have at least one date."]})

  for date in dates:
    sr = JobDateSerializer(data=date)
    sr.is_valid(raise_exception=True)

"""
Serializers
"""
class JobDateSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.JobDate
    fields = ['name', 'start_date', 'end_date']

class JobSerializer(serializers.ModelSerializer):
  dates = JobDateSerializer(many=True)

  class Meta:
    model = models.Job
    fields = ['can_be_done_remotely', 'dates', 'project', 'start_date', 'end_date']
    read_only_fields = ['start_date', 'end_date']
    extra_kwargs = {'project': {'write_only': True}}
    validators=[dates_validator]

  def create(self, validated_data):
    dates = validated_data.pop('dates')

    job = models.Job.objects.create(**validated_data)

    for date in dates:
      sr = JobDateSerializer(data=date)
      date_obj = sr.create(date)
      job.dates.add(date_obj)
    job.update_dates()

    return job
