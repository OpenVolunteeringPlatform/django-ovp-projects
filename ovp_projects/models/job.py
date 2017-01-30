from django.db import models
from django.utils.translation import ugettext_lazy as _

class JobDate(models.Model):
  name = models.CharField(_('Label'), blank=True, null=True, max_length=20)
  start_date = models.DateTimeField(_('Start date'))
  end_date = models.DateTimeField(_('End date'))
  job = models.ForeignKey('Job', models.CASCADE, blank=True, null=True, related_name='dates', verbose_name=_('job'))

  def __str__(self):
    start_date = self.start_date and self.start_date.strftime("%d/%m/%Y %T") or '#'
    end_date = self.end_date and self.end_date.strftime("%d/%m/%Y %T") or '#'
    return "{}: {} ~ {}".format(self.name, start_date, end_date)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('job date')
    verbose_name_plural = _('job dates')


class Job(models.Model):
  project = models.OneToOneField('Project', blank=True, null=True)
  start_date = models.DateTimeField(_('Start date'), blank=True, null=True)
  end_date = models.DateTimeField(_('End date'), blank=True, null=True)
  can_be_done_remotely = models.BooleanField(_('This job can be done remotely'), default=False)

  def __str__(self):
    name = self.project and self.project.name or _('Unbound Job')
    start_date = self.start_date and self.start_date.strftime("%d/%m/%Y") or ''
    end_date = self.end_date and self.end_date.strftime("%d/%m/%Y") or ''
    return "{}: {} ~ {}".format(name, start_date, end_date)

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

