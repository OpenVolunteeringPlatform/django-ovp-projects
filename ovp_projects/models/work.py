from django.db import models
from django.utils.translation import ugettext_lazy as _

WEEKDAYS = (
  (1, _('Monday')),
  (2, _('Tuesday')),
  (3, _('Wednesday')),
  (4, _('Thursday')),
  (5, _('Friday')),
  (6, _('Saturday')),
  (0, _('Sunday')),
)

PERIODS = (
  (0, _('Morning')),
  (1, _('Afternoon')),
  (2, _('Evening')),
)

class Availability(models.Model):
  weekday = models.PositiveSmallIntegerField(_('weekday'), choices=WEEKDAYS)
  period = models.PositiveSmallIntegerField(_('period'), choices=PERIODS)

  def __str__(self):
    return _('%(weekday)s at %(period)s') % {'weekday': self.get_weekday_display(), 'period': self.get_period_display()}

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('availability')
    verbose_name_plural = _('availabilities')



class Work(models.Model):
  project = models.OneToOneField('Project', blank=True, null=True)
  availabilities = models.ManyToManyField('Availability')
  weekly_hours = models.PositiveSmallIntegerField(_('Weekly hours'), blank=True, null=True)
  description = models.CharField(_('Description'), blank=True, null=True, max_length=4000)
  can_be_done_remotely = models.BooleanField(_('This work can be done remotely.'), default=False)

  def __str__(self):
    return "%s horas por semana" % (self.weekly_hours)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('work')
    verbose_name_plural = _('works')
