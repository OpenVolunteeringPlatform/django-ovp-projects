from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ovp_projects import emails

class Apply(models.Model):
  user = models.ForeignKey('ovp_users.User', blank=True, null=True)
  project = models.ForeignKey('ovp_projects.Project')
  status = models.CharField(_('name'), max_length=30)
  date = models.DateTimeField(auto_now_add=True, blank=True) # created date
  canceled = models.BooleanField(_("Canceled"), default=False)
  canceled_date = models.DateTimeField(_("Canceled date"), blank=True, null=True)
  email = models.CharField(_('Email'), max_length=200, blank=True, null=True)

  def mailing(self, async_mail=None):
    return emails.ApplyMail(self, async_mail)

  def save(self, *args, **kwargs):
    if self.canceled:
      self.canceled_date = timezone.now()
      self.status = 'unapplied'
      self.mailing().sendUnappliedToVolunteer({'apply': self})
      self.mailing().sendUnappliedToOwner({'apply': self})
    else:
      self.canceled_date = None
      self.status = 'applied'
      self.mailing().sendAppliedToVolunteer({'apply': self})
      self.mailing().sendAppliedToOwner({'apply': self})

    return_data = super(Apply, self).save(*args, **kwargs)

    # Updating project applied_count
    # get_volunteers_numbers return a function, so ()()
    self.project.applied_count = self.project.get_volunteers_numbers()()
    self.project.save()

    return return_data


  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('apply')
    verbose_name_plural = _('applies')
    unique_together = (("email", "project"), )

