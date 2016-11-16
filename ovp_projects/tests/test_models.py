# test job
# test work


from django.test import TestCase

from ovp_projects.models import Project
from ovp_projects.models import VolunteerRole
from ovp_users.models import User

class ProjectModelTestCase(TestCase):
  def test_project_return_owner_email_and_phone(self):
    """ Assert the methods .get_phone() and .get_email() return owner phone and email address """
    phone = "123456789"
    email = "test_returned@test.com"

    user = User.objects.create_user(email=email, password="test_returned")
    user.phone = phone
    user.save()

    project = Project(name="test project", slug="test slug", details="abc", description="abc", owner=user)
    project.save()

    self.assertTrue(project.get_phone() == phone)
    self.assertTrue(project.get_email() == email)

  def test_project_delete(self):
    """ Assert project delete method modifies .deleted and .published columns """
    user = User.objects.create_user(email="test_deleted@deleted.com", password="test_deleted")
    project = Project(name="test project", slug="test deleted", details="abc", description="abc", owner=user)
    project.published = True
    project.save()

    self.assertTrue(project.deleted == False)
    self.assertTrue(project.published == True)
    self.assertTrue(project.deleted_date == None)

    project.delete()

    self.assertTrue(project.deleted == True)
    self.assertTrue(project.published == False)
    self.assertTrue(project.deleted_date)

  def test_project_publish(self):
    """ Assert publishing a project updates .published_date """
    user = User.objects.create_user(email="test_published@date.com", password="test_published_date")
    project = Project(name="test project", slug="test published date", details="abc", description="abc", owner=user)
    project.save()
    self.assertTrue(project.published_date == None)

    project.published = True
    project.save()

    self.assertTrue(project.published_date)

  def test_project_close(self):
    """ Assert closing a project updates .closed_date """
    user = User.objects.create_user(email="test_close@date.com", password="test_close_date")
    project = Project(name="test project", slug="test close date", details="abc", description="abc", owner=user)
    project.save()
    self.assertTrue(project.closed_date == None)

    project.closed = True
    project.save()

    self.assertTrue(project.closed_date)

  def test_excerpt_from_details(self):
    """ Assert that if a project has no .description, it will use 100 chars from .details as an excerpt """
    details = ("a" * 100) + "b"
    expected_description = "a" * 100

    user = User.objects.create_user(email="test_excerpt@text.com", password="test_excerpt_text")
    project = Project(name="test project", slug="test excerpt text", details=details, owner=user)
    project.save()

    project = Project.objects.get(pk=project.id)
    self.assertTrue(project.description == expected_description)

  def test_str_method_returns_name(self):
    """ Assert that .__str__() method returns project name """
    user = User.objects.create_user(email="test_str@test.com", password="test_str_test")
    project = Project(name="test str", slug="test str test", details="abc", owner=user)
    project.save()

    self.assertTrue(project.__str__() == "test str")


class VolunteerRoleModelTestCase(TestCase):
  def test_str_method_returns_role_info(self):
    """ Assert that .__str__() method returns role info """
    role = VolunteerRole(name="test role", details="a", prerequisites="b", vacancies=5)
    role.save()

    self.assertTrue(role.__str__() == "test role - a - b (5 vacancies)")