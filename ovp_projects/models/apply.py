from django.db import models
from django.utils.translation import ugettext_lazy as _

class Apply(models.Model):
  user = models.ForeignKey('ovp_users.User', blank=True, null=True)
  project = models.ForeignKey('ovp_projects.Project')
  status = models.CharField(_('name'), max_length=30)
  date = models.DateTimeField(auto_now_add=True, blank=True) # created date
  canceled = models.BooleanField(_("Canceled"), default=False)
  canceled_date = models.DateTimeField(_("Canceled date"), blank=True, null=True)
  email = models.CharField(_('Email'), max_length=200, blank=True, null=True)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('apply')
    verbose_name_plural = _('applies')
    unique_together = (("email", "project"), )

#  def save(self, *args, **kwargs):
#    if self.canceled:
#      self.canceled_date = datetime.now().replace(tzinfo=pytz.timezone("America/Sao_Paulo"))
#    else:
#      self.canceled_date = None
#
#    return_data = super(Apply, self).save(*args, **kwargs)
#
#    # Updating project applied_count
#    # get_volunteers_numbers return a function, so ()()
#    self.project.applied_count = self.project.get_volunteers_numbers()()
#    self.project.save()
#
#    nonprofit = self.project.nonprofit
#    nonprofit.volunteer_count = nonprofit.get_volunteers_numbers()()
#    nonprofit.save()
#
#    return return_data
#
#  def __unicode__(self):
#    return "[%s] %s - %s" % (self.canceled, self.volunteer.user.name, self.project.name)
#
#  class Meta:
#    app_label = 'atados_core'
#    verbose_name = _('apply')
#    verbose_name_plural = _('applies')
