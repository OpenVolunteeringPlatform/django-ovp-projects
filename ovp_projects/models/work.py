from django.db import models
from django.utils.translation import ugettext_lazy as _


class Work(models.Model):
  project = models.OneToOneField('Project', blank=True, null=True)
  weekly_hours = models.PositiveSmallIntegerField(_('Weekly hours'), blank=True, null=True)
  description = models.CharField(_('Description'), max_length=4000)
  can_be_done_remotely = models.BooleanField(_("This job can be done remotely"), default=False)

  def __str__(self):
    return "%s hours per week" % (self.weekly_hours)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('work')
    verbose_name_plural = _('works')
