from django.test import TestCase
from django.core import mail
from django.test.utils import override_settings

from ovp_users.models import User
from ovp_projects.models import Project, Apply

class TestEmailTriggers(TestCase):
  def test_project_creation_trigger_email(self):
    """Assert that email is triggered when creating a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)

    mail.outbox = [] # Mails sent before creating don't matter
    project.save()

    self.assertTrue(len(mail.outbox) == 1)
    self.assertTrue(mail.outbox[0].subject == "Project created")

  def test_project_publishing_trigger_email(self):
    """Assert that email is triggered when publishing a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before publishing don't matter
    project.published = True
    project.save()

    self.assertTrue(len(mail.outbox) == 1)
    self.assertTrue(mail.outbox[0].subject == "Project published")


  def test_project_closing_trigger_email(self):
    """Assert that email is triggered when closing a project"""
    user = User.objects.create_user(email="test_project@project.com", password="test_project")
    project = Project(name="test project", slug="test project", details="abc", description="abc", owner=user)
    project.save()

    mail.outbox = [] # Mails sent before closing don't matter
    project.closed = True
    project.save()

    self.assertTrue(len(mail.outbox) == 1)
    self.assertTrue(mail.outbox[0].subject == "Project closed")


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

    self.assertTrue(len(mail.outbox) == 2)
    self.assertTrue(mail.outbox[0].subject == "Applied to project")
    self.assertTrue(mail.outbox[1].subject == "New volunteer")
    self.assertTrue("test_project@project.com" in recipients)
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

    self.assertTrue(len(mail.outbox) == 2)
    self.assertTrue(mail.outbox[0].subject == "Unapplied from project")
    self.assertTrue(mail.outbox[1].subject == "Volunteer unapplied from project")
    self.assertTrue("test_project@project.com" in recipients)
    self.assertTrue("test_volunteer@project.com" in recipients)
