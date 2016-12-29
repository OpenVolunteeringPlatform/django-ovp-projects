from django.test import TestCase
from django.core import mail
from django.test.utils import override_settings

from ovp_core.helpers import get_email_subject, is_email_enabled
from ovp_users.models import User
from ovp_projects.models import Project, Apply

class TestEmailTriggers(TestCase):
  def test_project_creation_trigger_email(self):
    """Assert that email is triggered when creating a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)

    mail.outbox = [] # Mails sent before creating don't matter
    project.save()

    if is_email_enabled("projectCreated"):
      self.assertTrue(len(mail.outbox) == 1)
      self.assertTrue(mail.outbox[0].subject == get_email_subject("projectCreated", "Project created"))
    else: # pragma: no cover
      self.assertTrue(len(mail.outbox) == 0)

  def test_project_publishing_trigger_email(self):
    """Assert that email is triggered when publishing a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before publishing don't matter
    project.published = True
    project.save()


    if is_email_enabled("projectPublished"): # pragma: no cover
      self.assertTrue(len(mail.outbox) == 1)
      self.assertTrue(mail.outbox[0].subject == get_email_subject("projectPublished", "Project published"))
    else: # pragma: no cover
      self.assertTrue(len(mail.outbox) == 0)


  def test_project_closing_trigger_email(self):
    """Assert that email is triggered when closing a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before closing don't matter
    project.closed = True
    project.save()


    if is_email_enabled("projectClosed"): # pragma: no cover
      self.assertTrue(len(mail.outbox) == 1)
      self.assertTrue(mail.outbox[0].subject == get_email_subject("projectClosed", "Project closed"))
    else: # pragma: no cover
      self.assertTrue(len(mail.outbox) == 0)


  def test_apply_trigger_email(self):
    """Assert that applying to project trigger one email to volunteer and one to project owner"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    volunteer = User.objects.create_user(email="test_volunteer@project.com", password="test_volunteer")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before applying don't matter
    apply = Apply(project=project, user=volunteer, email=volunteer.email)
    apply.save()

    recipients = [x.to[0] for x in mail.outbox]
    subjects = [x.subject for x in mail.outbox]

    if is_email_enabled("volunteerApplied-ToVolunteer"): # pragma: no cover
      self.assertTrue(get_email_subject("volunteerApplied-ToVolunteer", "Applied to project") in subjects)
      self.assertTrue("test_project@project.com" in recipients)

    if is_email_enabled("volunteerApplied-ToOwner"): # pragma: no cover
      self.assertTrue(get_email_subject("volunteerApplied-ToOwner", "New volunteer") in subjects)
      self.assertTrue("test_volunteer@project.com" in recipients)


  def test_unapply_trigger_email(self):
    """Assert that applying to project trigger one email to volunteer and one to project owner"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    volunteer = User.objects.create_user(email="test_volunteer@project.com", password="test_volunteer")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before applying don't matter
    apply = Apply(project=project, user=volunteer, email=volunteer.email, canceled=True)
    apply.save()

    recipients = [x.to[0] for x in mail.outbox]
    subjects = [x.subject for x in mail.outbox]

    if is_email_enabled("volunteerUnapplied-ToVolunteer"): # pragma: no cover
      self.assertTrue(get_email_subject("volunteerUnapplied-ToVolunteer", "Unapplied from project") in subjects)
      self.assertTrue("test_project@project.com" in recipients)

    if is_email_enabled("volunteerUnapplied-ToOwner"): # pragma: no cover
      self.assertTrue(get_email_subject("volunteerUnapplied-ToOwner", "Volunteer unapplied from project") in subjects)
      self.assertTrue("test_volunteer@project.com" in recipients)
