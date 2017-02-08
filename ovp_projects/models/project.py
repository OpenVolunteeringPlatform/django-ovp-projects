from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ovp_projects.models.apply import Apply
from ovp_projects import emails


class Project(models.Model):
  """
  Project model
  """
  image = models.ForeignKey('ovp_uploads.UploadedImage', blank=True, null=True, verbose_name=_('image'))
  address = models.OneToOneField('ovp_core.GoogleAddress', blank=True, null=True, verbose_name=_('address'))
  skills = models.ManyToManyField('ovp_core.Skill', verbose_name=_('skills'))
  causes = models.ManyToManyField('ovp_core.Cause', verbose_name=_('causes'))

  # Relationships
  owner = models.ForeignKey('ovp_users.User', verbose_name=_('owner'))
  organization = models.ForeignKey('ovp_organizations.Organization', blank=False, null=True, verbose_name=_('organization'))

  # Fields
  name = models.CharField(_('Project name'), max_length=100)
  slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
  published = models.BooleanField(_("Published"), default=False)
  highlighted = models.BooleanField(_("Highlighted"), default=False, blank=False)
  applied_count = models.IntegerField(_('Applied count'), blank=False, null=False, default=0)
  max_applies = models.IntegerField(blank=False, null=False, default=1) #note: This is not a hard limit, or is it?
  max_applies_from_roles = models.IntegerField(blank=False, null=False, default=0) # This is not a hard limit, just an estimate based on roles vacancies
  public_project = models.BooleanField(_("Public"), default=True, blank=False)
  minimum_age = models.IntegerField(_("Minimum Age"), blank=False, null=False, default=0)
  hidden_address = models.BooleanField(_('Hidden address'), default=False)

  # Date fields
  published_date = models.DateTimeField(_("Published date"), blank=True, null=True)
  closed = models.BooleanField(_("Closed"), default=False)
  closed_date = models.DateTimeField(_("Closed date"), blank=True, null=True)
  deleted = models.BooleanField(_("Deleted"), default=False)
  deleted_date = models.DateTimeField(_("Deleted date"), blank=True, null=True)
  created_date = models.DateTimeField(_('Created date'), auto_now_add=True)
  modified_date = models.DateTimeField(_('Modified date'), auto_now=True)

  # About
  details = models.TextField(_('Details'), max_length=3000)
  description = models.TextField(_('Short description'), max_length=160, blank=True, null=True)

  def mailing(self, async_mail=None):
    return emails.ProjectMail(self, async_mail)

  '''
  Data methods
  '''
  def get_phone(self):
    return self.owner.phone

  def get_email(self):
    return self.owner.email

  def get_volunteers_numbers(self):
    return Apply.objects.filter(project=self, canceled=False).count

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
        self.published_date = timezone.now()
        self.mailing().sendProjectPublished({'project': self})

      if not orig.closed and self.closed:
        self.closed_date = timezone.now()
        self.mailing().sendProjectClosed({'project': self})

      if not orig.deleted and self.deleted:
        self.deleted_date = timezone.now()
    else:
      # Project being created
      self.slug = self.generate_slug()
      self.mailing().sendProjectCreated({'project': self})

    # If there is no description, take 100 chars from the details
    if not self.description:
      if len(self.details) > 100:
        self.description = self.details[0:100]
      else:
        self.description = self.details

    self.modified_date = timezone.now()

    return super(Project, self).save(*args, **kwargs)

  def generate_slug(self):
    if self.name:
      slug = slugify(self.name)[0:99]
      append = ''
      i = 0

      query = Project.objects.filter(slug=slug + append)
      while query.count() > 0:
        i += 1
        append = '-' + str(i)
        query = Project.objects.filter(slug=slug + append)
      return slug + append
    return None

  def active_apply_set(self):
    return self.apply_set.filter(canceled=False)

  def __str__(self):
      return  '%s' % (self.name)

  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('project')
    verbose_name_plural = _('projects')


class VolunteerRole(models.Model):
  """
  Volunteer role model
  """
  name = models.CharField(_('Role name'), max_length=50, blank=True, null=True, default=None)
  prerequisites = models.TextField(_('Prerequisites'), max_length=1024, blank=True, null=True, default=None)
  details = models.TextField(_('Details'), max_length=1024, blank=True, null=True, default=None)
  vacancies = models.PositiveSmallIntegerField(_('Vacancies'), blank=True, null=True, default=None)
  project = models.ForeignKey(Project, blank=True, null=True, related_name='roles', verbose_name=_('Project'))


  class Meta:
    app_label = 'ovp_projects'
    verbose_name = _('volunteer role')
    verbose_name_plural = _('volunteer roles')

  def __str__(self):
    return  '%s - %s - %s (%s vacancies)' % (self.name, self.details, self.prerequisites, self.vacancies)



@receiver(post_save, sender=VolunteerRole)
@receiver(post_delete, sender=VolunteerRole)
def update_max_applies_from_roles(sender, **kwargs):
  if not kwargs.get('raw', False):
    project = kwargs['instance'].project

    if project:
      queryset = VolunteerRole.objects.filter(project=project)
      vacancies = queryset.aggregate(Sum('vacancies')).get('vacancies__sum')
      project.max_applies_from_roles = vacancies if vacancies else 0
      project.save()
