from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ovp_projects import emails

apply_status_choices = (
    ('applied', 'Applied'),
    ('unapplied', 'Canceled'),
)

class Apply(models.Model):
  user = models.ForeignKey('ovp_users.User', blank=True, null=True, verbose_name=_('user'))
  project = models.ForeignKey('ovp_projects.Project', verbose_name=_('project'))
  status = models.CharField(_('status'), max_length=30, choices=apply_status_choices, default="applied")
  date = models.DateTimeField(_('created date'), auto_now_add=True, blank=True)
  canceled = models.BooleanField(_("canceled"), default=False)
  canceled_date = models.DateTimeField(_("canceled date"), blank=True, null=True)

  username = models.CharField(_('name'), max_length=200, blank=True, null=True)
  email = models.CharField(_('email'), max_length=190, blank=True, null=True)
  phone = models.CharField(_('phone'), max_length=30, blank=True, null=True)

  def __init__(self, *args, **kwargs):
    super(Apply, self).__init__(*args, **kwargs)
    self.__original_status = self.status
    self.__original_canceled = self.canceled

  def mailing(self, async_mail=None):
    return emails.ApplyMail(self, async_mail)

  def save(self, *args, **kwargs):

    if self.pk == None:
      # Object being created
      self.mailing().sendAppliedToVolunteer({'apply': self})
      self.mailing().sendAppliedToOwner({'apply': self})
    else:
      # Object being updated
      if self.__original_canceled != self.canceled:
        # self.canceled was modified
        if self.canceled == True:
          self.status = "unapplied"
        if self.canceled == False:
          self.status = "applied"

      # Status can be set without modifying .canceled directly
      # Therefore we reset values checked on the previous ifs
      if self.__original_status != self.status:
        if self.status == "unapplied":
          self.canceled = True
          self.canceled_date = timezone.now()
          self.mailing().sendUnappliedToVolunteer({'apply': self})
          self.mailing().sendUnappliedToOwner({'apply': self})
        else:
          self.canceled = False
          self.canceled_date = None

    # Update original values
    self.__original_status = self.status
    self.__original_canceled = self.canceled
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

