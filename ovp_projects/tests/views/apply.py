from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_projects.models import Project, Apply
from ovp_users.models import User
from ovp_organizations.models import Organization

from collections import OrderedDict

class ApplyAndUnapplyTestCase(TestCase):
  def test_can_apply_to_project(self):
    """Assert that authenticated user can apply to project"""
    owner = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=owner)
    project.save()

    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    response = client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["non_field_errors"][0] == "The fields email, project must make a unique set.")

    response = client.get(reverse("project-detail", ["test-project"]), format="json")
    self.assertTrue(type(response.data["applies"][0]["user"]) in [dict, OrderedDict])


  def test_can_reapply_to_project(self):
    """Assert that user can reapply to a project"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    # Apply
    response = client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    project = Project.objects.get(slug="test-project")
    self.assertTrue(project.applied_count == 1)

    # Unapply
    response = client.post(reverse("project-applies-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully unapplied.")

    a = Apply.objects.last()
    self.assertTrue(a.canceled == True)
    self.assertTrue(a.canceled_date)

    project = Project.objects.get(slug="test-project")
    self.assertTrue(project.applied_count == 0)

    # Reapply
    response = client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    project = Project.objects.get(slug="test-project")
    self.assertTrue(project.applied_count == 1)

    a = Apply.objects.last()
    self.assertTrue(a.canceled == False)
    self.assertTrue(a.canceled_date == None)

  def test_cant_unapply_if_not_apply_or_unauthenticated(self):
    """Assert that user can't unapply if not already applied or unauthenticated"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()

    response = client.post(reverse("project-applies-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Authentication credentials were not provided.")
    self.assertTrue(response.status_code == 401)

    client.force_authenticate(user=user)
    response = client.post(reverse("project-applies-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "This is user is not applied to this project.")
    self.assertTrue(response.status_code == 400)

  def test_cant_apply_to_inexistent_project(self):
    """Assert that user can't apply to inexistent project"""
    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Not found.")
    self.assertTrue(response.status_code == 404)


  @override_settings(OVP_PROJECTS={"UNAUTHENTICATED_APPLY": False})
  def test_unauthenticated_user_cant_apply_to_project(self):
    """Assert that unauthenticated user cant apply to project"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse("project-applies-apply", ["test-project"]), {"email": "testemail@test.com"}, format="json")
    self.assertTrue(response.data["detail"] == "Authentication credentials were not provided.")
    self.assertTrue(response.status_code == 401)


  @override_settings(OVP_PROJECTS={"UNAUTHENTICATED_APPLY": True})
  def test_unauthenticated_user_can_apply_to_project(self):
    """Assert that unauthenticated user can apply to project if properly configured"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse("project-applies-apply", ["test-project"]), {"email": "testemail@test.com"}, format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)


class ProjectAppliesRetrievingTestCase(TestCase):
  def setUp(self):
    # Create project
    self.owner = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    self.project = Project(name="test project", details="abc", description="abc", owner=self.owner)
    self.project.save()

    # Apply
    self.applier = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")
    self.client = APIClient()
    self.client.force_authenticate(user=self.applier)
    response = self.client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

  def _assert_apply_response_data(self, response):
    self.assertTrue("email" in response.data[0])
    self.assertTrue("date" in response.data[0])
    self.assertTrue("canceled" in response.data[0])
    self.assertTrue("canceled_date" in response.data[0])
    self.assertTrue("status" in response.data[0])
    self.assertTrue("name" in response.data[0]["user"])
    self.assertTrue("avatar" in response.data[0]["user"])
    self.assertTrue("email" in response.data[0]["user"])
    self.assertTrue("phone" in response.data[0]["user"])

  def test_project_owner_can_read_applies(self):
    """Assert that project owner can retrieve project applies"""
    self.client.force_authenticate(user=self.owner)
    response = self.client.get(reverse("project-applies-list", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 200)
    self._assert_apply_response_data(response)

  def test_retrieving_applies_as_csv(self):
    """Assert it's possible to retrieve applies in CSV format"""
    # Read applies in csv format
    self.client.force_authenticate(user=self.owner)
    response = self.client.get(reverse("project-applies-list", ["test-project", "csv"]), format="csv")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(response["Content-Type"] == "text/csv; charset=utf-8")

  def test_cant_retrieve_applies_while_unauthorized(self):
    """Assert that a user who is not project owner or organization owner/member can't read project applies"""
    response = self.client.get(reverse("project-applies-list", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 403)

    self.client.force_authenticate(user=self.applier)
    response = self.client.get(reverse("project-applies-list", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 403)

  def test_cant_retrieve_applies_for_inexistent_project(self):
    """Assert that a user who is not project owner or organization owner/member can't read project applies"""
    self.client.force_authenticate(user=self.owner)
    response = self.client.get(reverse("project-applies-list", ["inexistent"]), format="json")
    self.assertTrue(response.status_code == 404)


class ProjectApplyStatusUpdateTestCase(TestCase):
  def setUp(self):
    # Create organization
    self.organization_owner = User.objects.create_user(email="organization_owner@gmail.com", password="test_owner")
    self.organization_member = User.objects.create_user(email="organization_member@gmail.com", password="test_member")
    self.organization = Organization(name="test", type=0, owner=self.organization_owner)
    self.organization.save()
    self.organization.members.add(self.organization_member)

    # Create project
    self.project_owner = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    self.project = Project(name="test project", details="abc", description="abc", owner=self.project_owner, organization=self.organization)
    self.project.save()

    # Apply
    self.applier = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")
    self.client = APIClient()
    self.client.force_authenticate(user=self.applier)
    response = self.client.post(reverse("project-applies-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    # Get apply
    self.apply_id = Apply.objects.last().pk

  def _assert_can_update_apply(self):
    # Update apply
    data = {"status": "unapplied"}
    response = self.client.patch(reverse("project-applies-detail", ["test-project", self.apply_id]), data=data, format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["status"] == "unapplied")

    # Get apply
    response = self.client.get(reverse("project-applies-list", ["test-project"]), format="json")
    self.assertTrue(response.data[0]["status"] == "Canceled")

  def test_project_owner_can_update_apply_status(self):
    """Assert that project owner can update apply status"""
    self.client.force_authenticate(user=self.project_owner)
    self._assert_can_update_apply()

  def test_organization_owner_can_update_apply_status(self):
    """Assert that organization owner can update apply status"""
    self.client.force_authenticate(user=self.organization_owner)
    self._assert_can_update_apply()

  def test_organization_member_can_update_apply_status(self):
    """Assert that organization member can update apply status"""
    self.client.force_authenticate(user=self.organization_member)
    self._assert_can_update_apply()

  def test_unauthorized_user_cant_update_status(self):
    """Assert that organization member can update apply status"""
    client = APIClient()
    response = self.client.patch(reverse("project-applies-detail", ["test-project", self.apply_id]), data={"status": "unapplied"}, format="json")
    self.assertTrue(response.status_code == 403)

    client.force_authenticate(user=self.applier)
    response = self.client.patch(reverse("project-applies-detail", ["test-project", self.apply_id]), data={"status": "unapplied"}, format="json")
    self.assertTrue(response.status_code == 403)

  def test_update_to_invalid_status(self):
    """Assert that it's not possible to update to invalid apply status"""
    self.client.force_authenticate(user=self.project_owner)
    response = self.client.patch(reverse("project-applies-detail", ["test-project", self.apply_id]), data={"status": "invalid-status"}, format="json")
    self.assertTrue(response.status_code == 400)
    self.assertTrue(response.data["status"] == ["\"invalid-status\" is not a valid choice."])
