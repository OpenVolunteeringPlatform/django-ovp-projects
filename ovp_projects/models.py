from django.db import models
from django.utils import timezone
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

class Project(models.Model):
  """
  Project model
  """
  image = models.ForeignKey('ovp_uploads.UploadedImage')
  address = models.OneToOneField('ovp_core.GoogleAddress', blank=True, null=True)
  skills = models.ManyToManyField('ovp_core.Skill')
  causes = models.ManyToManyField('ovp_core.Cause')

  # Relationships
  owner = models.ForeignKey('ovp_users.User')
  organization = models.ForeignKey('ovp_organizations.Organization')
  roles = models.ManyToManyField('Role', verbose_name=_("Roles"), blank=True)

  # Fields
  name = models.CharField(_('Project name'), max_length=100)
  slug = models.SlugField(max_length=100, unique=True)
  published = models.BooleanField(_("Published"), default=False)
  highlighted = models.BooleanField(_("Highlighted"), default=False, blank=False)

  # Date fields
  published_date = models.DateTimeField(_("Published date"), blank=True, null=True)
  closed = models.BooleanField(_("Closed"), default=False)
  closed_date = models.DateTimeField(_("Closed date"), blank=True, null=True)
  deleted = models.BooleanField(_("Deleted"), default=False)
  deleted_date = models.DateTimeField(_("Deleted date"), blank=True, null=True)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)

  # About
  details = models.TextField(_('Details'), max_length=3000)
  description = models.TextField(_('Short description'), max_length=160, blank=True, null=True)


  '''
  Data methods
  '''
  def get_phone(self):
# return resposible phone
    pass

  def get_email(self):
# return resposible email
    pass

  '''
  Model operation methods
  '''
  def delete(self, *args, **kwargs):
      self.deleted = True
      self.published = False
      self.save()

  def save(self, *args, **kwargs):
    if self.pk is not None:
        orig = Project.objects.get(pk=self.pk)
        if not orig.published and self.published:
          self.published_date = datetime.now()
        if not orig.closed and self.closed:
          self.closed_date = datetime.now()
        if not orig.deleted and self.deleted:
          self.deleted_date = datetime.now()

    # If there is no description, take 100 chars from the details
    if not self.description and len(self.details) > 100:
      self.description = self.details[0:100]

    self.modified_date = timezone.now()

    return super(Project, self).save(*args, **kwargs)

  def __str__(self):
      return  '%s' % (self.name)


class Role(models.Model):
  """
  Project roles model
  """
  name = models.CharField(_('Role name'), max_length=50, blank=True, null=True, default=None)
  prerequisites = models.TextField(_('Prerequisites'), max_length=1024, blank=True, null=True, default=None)
  details = models.TextField(_('Details'), max_length=1024, blank=True, null=True, default=None)
  vacancies = models.PositiveSmallIntegerField(_('Vacancies'), blank=True, null=True, default=None)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('role')
    verbose_name_plural = _('roles')

  def __str__(self):
    return  '%s - %s - %s (%s vacancies)' % (self.name, self.details, self.prerequisites, self.vacancies)


class Availability(models.Model):
  weekday = models.PositiveSmallIntegerField(_('weekday'), choices=WEEKDAYS)
  period = models.PositiveSmallIntegerField(_('period'), choices=PERIODS)

  def __str__(self):
    return _('%(weekday)s at %(period)s') % {'weekday': self.get_weekday_display(), 'period': self.get_period_display()}

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('availability')


class Work(models.Model):
  project = models.OneToOneField(Project, blank=True, null=True)
  availabilities = models.ManyToManyField(Availability)
  weekly_hours = models.PositiveSmallIntegerField(_('Weekly hours'), blank=True, null=True)
  description = models.CharField(_('Description'), blank=True, null=True, max_length=4000)
  can_be_done_remotely = models.BooleanField(_('This work can be done remotely.'), default=False)

  def __str__(self):
    return "%s horas por semana" % (self.weekly_hours)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('work')
    verbose_name_plural = _('works')


class JobDate(models.Model):
  name = models.CharField(_("Start date"), blank=True, null=True, max_length=20)
  start_date = models.DateTimeField(_("Start date"), blank=True, null=True)
  end_date = models.DateTimeField(_("End date"), blank=True, null=True)


class Job(models.Model):
  project = models.OneToOneField(Project, blank=True, null=True)
  start_date = models.DateTimeField(_("Start date"), blank=True, null=True)
  end_date = models.DateTimeField(_("End date"), blank=True, null=True)
  can_be_done_remotely = models.BooleanField(_("This job can be done remotely"), default=False)
  dates = models.ManyToManyField('JobDate', blank=True)

  def __str__(self):
    return "%s - %s" % (self.start_date, self.end_date)

  def update_dates(self):
    start = self.dates.all().order_by('start_date').first().start_date
    end   = self.dates.all().order_by('-end_date').first().end_date
    self.start_date = start
    self.end_date = end
    self.save()

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('Job')
    verbose_name_plural = _('Jobs')
