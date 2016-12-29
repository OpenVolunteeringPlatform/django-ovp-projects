from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_projects.models import Project, Apply
from ovp_users.models import User
from ovp_organizations.models import Organization

from collections import OrderedDict

import json
import copy


base_project = {"name": "test project", "slug": "test-cant-override-slug-on-creation", "details": "this is just a test project", "description": "the project is being tested", "address": {"typed_address": "r. tecainda, 81, sao paulo"}, "disponibility": {"type": "work", "work": {"description": "abc"}}}

@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": True})
class ProjectResourceViewSetTestCase(TestCase):
  def test_cant_create_project_unauthenticated(self):
    """Assert that it's not possible to create a project while unauthenticated"""
    client = APIClient()
    response = client.post(reverse("project-list"), {}, format="json")

    self.assertTrue(response.data["detail"] == "Authentication credentials were not provided.")
    self.assertTrue(response.status_code == 401)

  def test_can_create_project(self):
    """Assert that it's possible to create a project while authenticated"""
    user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")

    data = copy.copy(base_project)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("project-list"), data, format="json")

    self.assertTrue(response.status_code == 201)
    self.assertTrue(response.data["id"])
    self.assertTrue(response.data["name"] == data["name"])
    self.assertTrue(response.data["slug"] == "test-project")
    self.assertTrue(response.data["details"] == data["details"])
    self.assertTrue(response.data["description"] == data["description"])

    project = Project.objects.get(pk=response.data["id"])
    self.assertTrue(project.owner.id == user.id)
    self.assertTrue(project.address.typed_address == data["address"]["typed_address"])


  def test_cant_create_project_empty_name(self):
    """Assert that it's not possible to create a project with empty name"""
    user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")

    client = APIClient()
    client.force_authenticate(user=user)

    data = copy.copy(base_project)
    data["name"] = ""

    response = client.post(reverse("project-list"), data, format="json")
    self.assertTrue(response.data["name"][0] == "This field may not be blank.")


  def test_project_retrieval(self):
    """Assert projects can be retrieved"""
    user = User.objects.create_user(email="test_retrieval@gmail.com", password="testretrieval")

    client = APIClient()
    client.force_authenticate(user=user)

    data = copy.copy(base_project)
    response = client.post(reverse("project-list"), data, format="json")

    response = client.get(reverse("project-detail", ["test-project"]), format="json")

    self.assertTrue(response.data["name"] == data["name"])
    self.assertTrue(response.data["slug"] == "test-project")
    self.assertTrue(response.data["details"] == data["details"])
    self.assertTrue(response.data["description"] == data["description"])
    self.assertTrue(response.data["published"] == False)
    self.assertTrue(type(response.data["owner"]) in [dict, OrderedDict])
    self.assertTrue(type(response.data["applies"]) is list)
    self.assertTrue(type(response.data["applied_count"]) is int)
    self.assertTrue(type(response.data["max_applies_from_roles"]) is int)



@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": True})
class ProjectCloseTestCase(TestCase):
  def setUp(self):
    user = User.objects.create_user(email="test_close@gmail.com", password="testclose")
    self.client = APIClient()
    self.client.force_authenticate(user=user)

    data = copy.copy(base_project)
    self.project = self.client.post(reverse("project-list"), data, format="json")

  def test_cant_close_project_if_not_owner_or_organization_member(self):
    """ Assert that it's not possible to close a project if not the owner or organization member """
    user = User.objects.create_user(email="otheruser@gmail.com", password="otheruser")
    self.client.force_authenticate(user=user)
    response = self.client.post(reverse("project-close", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 403)


  def test_can_close_project(self):
    """ Assert that it's possible to close a project """
    response = self.client.post(reverse("project-close", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["closed"] == True)
    self.assertTrue(response.data["closed"])


@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": False})
class ProjectWithOrganizationTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")
    self.another_user = User.objects.create_user(email="test_another_user@test.com", password="testcancreate")
    self.data = copy.copy(base_project)
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

  def test_no_organization(self):
    """Test no organization returns error"""
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["organization"] == ["This field is required."])
    self.assertTrue(response.status_code == 400)

  def test_organization_is_int(self):
    """Test organization field must be int"""
    self.data['organization'] = 'str'

    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["organization"] == ["Incorrect type. Expected pk value, received str."])
    self.assertTrue(response.status_code == 400)

  def test_user_is_owner_or_member(self):
    """Test user is owner or member of organization"""
    wrong_org = Organization(name="test", type=0, owner=self.another_user)
    wrong_org.save()

    self.data['organization'] = wrong_org.pk
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 403)

  @override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_IN_ANY_ORGANIZATION": True})
  def test_can_create_in_any_organization_if_settings_allow(self):
    """Test user can create project inside any organization if properly configured"""
    wrong_org = Organization(name="test", type=0, owner=self.another_user)
    wrong_org.save()

    self.data['organization'] = wrong_org.pk
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)

  def test_can_create(self):
    """Test user can create project with valid organization"""
    org = Organization(name="test", type=0, owner=self.user)
    org.save()
    org.members.add(self.another_user)

    self.data['organization'] = org.pk
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)

    self.client.force_authenticate(self.another_user)
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)


class ManageableProjectsRouteTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")
    self.user.save()
    self.user2 = User.objects.create_user(email="test_can_create_project2@gmail.com", password="testcancreate")
    self.user2.save()
    self.organization = Organization(name="test", type=0, owner=self.user)
    self.organization.save()
    self.organization2 = Organization(name="test2", type=0, owner=self.user2)
    self.organization2.save()
    self.organization2.members.add(self.user)

    p = Project(name="test project 1", owner=self.user)
    p.save()

    p = Project(name="test project 2", owner=self.user, organization=self.organization)
    p.save()

    p = Project(name="test project 3", owner=self.user2, organization=self.organization2)
    p.save()

    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

  def test_requires_authentication(self):
    """Test hitting route unauthenticated returns 401"""
    client = APIClient()
    response = client.get(reverse("project-manageable"), {}, format="json")
    self.assertTrue(response.status_code == 401)


  def test_returns_projects(self):
    """Test hitting route authenticated returns projects"""
    response = self.client.get(reverse("project-manageable"), {}, format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(len(response.data) == 3)


@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": True})
class ProjectResourceUpdateTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")
    self.data = copy.copy(base_project)
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)

  def test_wrong_user_cant_update(self):
    """Test only owner can update project"""
    wrong_user = User.objects.create_user(email="wrong_user@gmail.com", password="testcancreate")
    wrong_user.save()
    self.client.force_authenticate(user=wrong_user)

    response = self.client.patch(reverse("project-detail", ["test-project"]), {}, format="json")
    self.assertTrue(response.status_code == 403)

  def test_update_fields(self):
    """Test patch request update fields"""
    updated_project = {"name": "test update", "details": "update", "description": "update"}
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["name"] == "test update")
    self.assertTrue(response.data["details"] == "update")
    self.assertTrue(response.data["description"] == "update")

    user = User.objects.create_user(email="another@user.com", password="testcancreate")
    organization = Organization(name="test", type=0, owner=self.user)
    organization.save()
    organization.members.add(user)
    project = Project.objects.get(pk=response.data['id'])
    project.organization = organization
    project.save()
    self.client.force_authenticate(user)
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")
    self.assertTrue(response.status_code == 200)

  def test_update_address(self):
    """Test patch request update address resource"""
    updated_project = {"address": {"typed_address": "r. capote valente, 701, sao paulo"}}
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")

    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["address"]["typed_address"] == "r. capote valente, 701, sao paulo")

  def test_update_disponibility(self):
    """Test patch request update disponibility resource"""
    updated_project = {"disponibility": {"type": "job", "job": {"dates": [{"name": "update", "start_date": "2013-01-29T12:34:56.123Z", "end_date": "2013-01-29T13:34:56.123Z"}, {"name": "test1", "start_date": "2013-02-01T12:34:56.123Z", "end_date": "2013-02-01T13:34:56.123Z"}]}}}
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")

    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["disponibility"]["type"] == "job")
    self.assertTrue(response.data["disponibility"]["job"]["dates"][0]["name"] == "update")


    updated_project = {"disponibility": {"type": "work", "work": {"description": "update"}}}
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")

    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["disponibility"]["type"] == "work")
    self.assertTrue(response.data["disponibility"]["work"]["description"] == "update")

  def test_update_roles(self):
    """Test patch request update roles resource"""
    updated_project = {"roles": [{"name": "test", "prerequisites": "test2", "details": "test3", "vacancies": 5}]}
    response = self.client.patch(reverse("project-detail", ["test-project"]), updated_project, format="json")

    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["roles"] == updated_project["roles"])


@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": True})
class DisponibilityTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")
    self.data = copy.copy(base_project)
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)

  def test_no_disponibility(self):
    """Test no disponibility returns error"""
    del self.data["disponibility"]
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"] == ["This field is required."])
    self.assertTrue(response.status_code == 400)

  def test_disponibility_type_required(self):
    """Test disponibility type is required"""
    self.data["disponibility"] = {}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["type"] == ["This field is required."])
    self.assertTrue(response.status_code == 400)

  def test_type_not_work_or_job(self):
    """Test disponibility type can't be different than work or job"""
    self.data["disponibility"] = {"type": "test"}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["type"] == ["Must have either be 'work' or 'job'."])
    self.assertTrue(response.status_code == 400)

  def test_empty_job_or_work(self):
    """Test empty job or work returns error"""
    self.data["disponibility"] = {"type": "job"}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["job"] == ["This field is required if type=\"job\"."])
    self.assertTrue(response.status_code == 400)

    self.data["disponibility"] = {"type": "work"}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["work"] == ["This field is required if type=\"work\"."])
    self.assertTrue(response.status_code == 400)

  def test_work_description_required(self):
    """Test work description is required"""
    self.data["disponibility"] = {"type": "work", "work": {}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["work"]["description"] == ["This field is required."])
    self.assertTrue(response.status_code == 400)

  def test_correct_work(self):
    """Test correct work returns success"""
    self.data["disponibility"] = {"type": "work", "work": {"description": "test desc", "weekly_hours": 6}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["type"] == "work")
    self.assertTrue(response.data["disponibility"]["work"]["description"] == "test desc")
    self.assertTrue(response.data["disponibility"]["work"]["weekly_hours"] == 6)
    self.assertTrue(response.status_code == 201)

  def test_job_dates_required(self):
    """Test job dates is required"""
    self.data["disponibility"] = {"type": "job", "job": {}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["job"]["dates"] == ["This field is required."])
    self.assertTrue(response.status_code == 400)

  def test_job_dates_cant_be_empty(self):
    """Test job dates can't be empty"""
    self.data["disponibility"] = {"type": "job", "job": {"dates": []}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["job"]["dates"] == ["Must have at least one date."])
    self.assertTrue(response.status_code == 400)

  def test_job_dates_cant_be_wrong_type(self):
    """Test job dates can't be wrong type"""
    self.data["disponibility"] = {"type": "job", "job": {"dates": ''}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["job"]["dates"]["non_field_errors"] == ["Expected a list of items but got type \"str\"."])
    self.assertTrue(response.status_code == 400)

  def test_job_dates_cant_have_bad_formatted_date(self):
    """Test job dates can't have bad formatted date"""
    self.data["disponibility"] = {"type": "job", "job": {"dates": [{"start_date": "abc", "end_date": "abc"}]}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["disponibility"]["job"]["dates"][0]["start_date"] == ["Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."])
    self.assertTrue(response.data["disponibility"]["job"]["dates"][0]["end_date"] == ["Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."])
    self.assertTrue(response.status_code == 400)

  def test_job_returns_success(self):
    """Test correct job returns success"""
    self.data["disponibility"] = {"type": "job", "job": {"dates": [{"name": "test1", "start_date": "2013-01-29T12:34:56.123Z", "end_date": "2013-01-29T13:34:56.123Z"}, {"name": "test1", "start_date": "2013-02-01T12:34:56.123Z", "end_date": "2013-02-01T13:34:56.123Z"}]}}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)
    self.assertTrue(response.data["disponibility"]["job"]["dates"][0]["start_date"] == "2013-01-29T12:34:56.123000Z")
    self.assertTrue(response.data["disponibility"]["job"]["dates"][0]["end_date"] == "2013-01-29T13:34:56.123000Z")
    self.assertTrue(response.data["disponibility"]["job"]["dates"][1]["start_date"] == "2013-02-01T12:34:56.123000Z")
    self.assertTrue(response.data["disponibility"]["job"]["dates"][1]["end_date"] == "2013-02-01T13:34:56.123000Z")

    self.assertTrue(response.data["disponibility"]["job"]["start_date"] == "2013-01-29T12:34:56.123000Z")
    self.assertTrue(response.data["disponibility"]["job"]["end_date"] == "2013-02-01T13:34:56.123000Z")



@override_settings(OVP_PROJECTS={"CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION": True})
class VolunteerRoleTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")
    self.data = copy.copy(base_project)
    self.client = APIClient()
    self.client.force_authenticate(user=self.user)


  def test_roles_is_correct_type(self):
    """Test roles is correct type"""
    self.data["roles"] = {"name": "test", "prerequisites": "test2", "details": "test3", "vacancies": 5}
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.data["roles"]["non_field_errors"] == ["Expected a list of items but got type \"dict\"."])
    self.assertTrue(response.status_code == 400)


  def test_roles_get_saved(self):
    """Test roles get saved"""
    self.data["roles"] = [{"name": "test", "prerequisites": "test2", "details": "test3", "vacancies": 5}]
    response = self.client.post(reverse("project-list"), self.data, format="json")
    self.assertTrue(response.status_code == 201)
    self.assertTrue(response.data["roles"] == self.data["roles"])

    response = self.client.get(reverse("project-detail", ['test-project']), format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue(response.data["roles"] == self.data["roles"])



class ApplyTestCase(TestCase):
  def test_can_apply_to_project(self):
    """Assert that authenticated user can apply to project"""
    owner = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=owner)
    project.save()

    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("project-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    response = client.post(reverse("project-apply", ["test-project"]), format="json")
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
    response = client.post(reverse("project-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)

    project = Project.objects.get(slug="test-project")
    self.assertTrue(project.applied_count == 1)

    # Unapply
    response = client.post(reverse("project-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully unapplied.")

    a = Apply.objects.last()
    self.assertTrue(a.canceled == True)
    self.assertTrue(a.canceled_date)

    project = Project.objects.get(slug="test-project")
    self.assertTrue(project.applied_count == 0)

    # Reapply
    response = client.post(reverse("project-apply", ["test-project"]), format="json")
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

    response = client.post(reverse("project-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Authentication credentials were not provided.")
    self.assertTrue(response.status_code == 401)

    client.force_authenticate(user=user)
    response = client.post(reverse("project-unapply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "This is user is not applied to this project.")
    self.assertTrue(response.status_code == 400)

  def test_cant_apply_to_inexistent_project(self):
    """Assert that user can't apply to inexistent project"""
    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("project-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Not found.")
    self.assertTrue(response.status_code == 404)


  def test_unauthenticated_user_cant_apply_to_project(self):
    """Assert that unauthenticated user cant apply to project"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse("project-apply", ["test-project"]), {"email": "testemail@test.com"}, format="json")
    self.assertTrue(response.data["detail"] == "Authentication credentials were not provided.")
    self.assertTrue(response.status_code == 401)


  @override_settings(OVP_PROJECTS={"UNAUTHENTICATED_APPLY": True})
  def test_unauthenticated_user_can_apply_to_project(self):
    """Assert that unauthenticated user can apply to project if properly configured"""
    user = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse("project-apply", ["test-project"]), {"email": "testemail@test.com"}, format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)


  def test_can_read_applies(self):
    """Assert that organization member can view project applies"""
    owner = User.objects.create_user(email="owner_user@gmail.com", password="test_owner")
    project = Project(name="test project", details="abc", description="abc", owner=owner)
    project.save()

    user = User.objects.create_user(email="apply_user@gmail.com", password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(reverse("project-apply", ["test-project"]), format="json")
    self.assertTrue(response.data["detail"] == "Successfully applied.")
    self.assertTrue(response.status_code == 200)


    client = APIClient()
    client.force_authenticate(user=owner)
    response = client.get(reverse("project-applies", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 200)
    self.assertTrue("email" in response.data[0])
    self.assertTrue("date" in response.data[0])
    self.assertTrue("canceled" in response.data[0])
    self.assertTrue("canceled_date" in response.data[0])
    self.assertTrue("status" in response.data[0])
    self.assertTrue("name" in response.data[0]["user"])
    self.assertTrue("avatar" in response.data[0]["user"])
    self.assertTrue("email" in response.data[0]["user"])
    self.assertTrue("phone" in response.data[0]["user"])

    url = reverse("project-applies", ["test-project", "csv"])
    response = client.get(url, format="csv")
    self.assertTrue(response.status_code == 200)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(reverse("project-applies", ["test-project"]), format="json")
    self.assertTrue(response.status_code == 403)
