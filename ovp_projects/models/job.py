from django.db import models
from django.utils.translation import ugettext_lazy as _

class JobDate(models.Model):
  name = models.CharField(_("Start date"), blank=True, null=True, max_length=20)
  start_date = models.DateTimeField(_("Start date"))
  end_date = models.DateTimeField(_("End date"))

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('job date')
    verbose_name_plural = _('job dates')


class Job(models.Model):
  project = models.OneToOneField('Project', blank=True, null=True)
  start_date = models.DateTimeField(_("Start date"), blank=True, null=True)
  end_date = models.DateTimeField(_("End date"), blank=True, null=True)
  can_be_done_remotely = models.BooleanField(_("This job can be done remotely"), default=False)
  dates = models.ManyToManyField('JobDate', blank=True)

  def __str__(self):
    return "{} - {}".format(self.start_date, self.end_date)

  def update_dates(self):
    start = self.dates.all().order_by('start_date').first().start_date
    end   = self.dates.all().order_by('-end_date').first().end_date
    self.start_date = start
    self.end_date = end
    self.save()

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('job')
    verbose_name_plural = _('jobs')
