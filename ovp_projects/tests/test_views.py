# test project resource edit
# test project resource delete
# test is part of organization to create, edit
# test must be owner to delete project

# test unapply

from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_projects.models import Project, Apply
from ovp_users.models import User

import json


class ProjectResourceViewSetTestCase(TestCase):
  def test_cant_create_project_unauthenticated(self):
    """Assert that it's not possible to create a project while unauthenticated"""
    client = APIClient()
    response = client.post(reverse('project-list'), {}, format='json')

    self.assertTrue(response.data['detail'] == 'Authentication credentials were not provided.')
    self.assertTrue(response.status_code == 401)

  def test_can_create_project(self):
    """Assert that it's possible to create a project while authenticated"""
    user = User.objects.create_user(email="test_can_create_project@gmail.com", password="testcancreate")

    client = APIClient()
    client.force_authenticate(user=user)

    data = {'name': 'test project', 'slug': 'test-project', 'details': 'this is just a test project', 'description': 'the project is being tested', 'address': {'typed_address': 'r. tecainda, 81, sao paulo'}}
    response = client.post(reverse('project-list'), data, format='json')

    self.assertTrue(response.data['id'])
    self.assertTrue(response.data['name'] == data['name'])
    self.assertTrue(response.data['slug'] == data['slug'])
    self.assertTrue(response.data['details'] == data['details'])
    self.assertTrue(response.data['description'] == data['description'])

    project = Project.objects.get(pk=response.data['id'])
    self.assertTrue(project.owner.id == user.id)
    self.assertTrue(project.address.typed_address == data['address']['typed_address'])


  def test_project_retrieval(self):
    """Assert projects can be retrieved"""
    user = User.objects.create_user(email="test_retrieval@gmail.com", password="testretrieval")

    client = APIClient()
    client.force_authenticate(user=user)

    data = {'name': 'test project', 'slug': 'test-project', 'details': 'this is just a test project', 'description': 'the project is being tested', 'address': {'typed_address': 'r. tecainda, 81, sao paulo'}}
    response = client.post(reverse('project-list'), data, format='json')

    response = client.get(reverse('project-detail', ['test-project']), format='json')

    self.assertTrue(response.data['name'] == data['name'])
    self.assertTrue(response.data['slug'] == data['slug'])
    self.assertTrue(response.data['details'] == data['details'])
    self.assertTrue(response.data['description'] == data['description'])



class ApplyTestCase(TestCase):
  def test_can_apply_to_project(self):
    """Assert that authenticated user can apply to project"""
    user = User.objects.create_user(email='owner_user@gmail.com', password="test_owner")
    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user)
    project.save()

    user = User.objects.create_user(email='apply_user@gmail.com', password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse('project-apply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Successfully applied.')
    self.assertTrue(response.status_code == 200)

    response = client.post(reverse('project-apply', ['test-slug']), format='json')
    self.assertTrue(response.data['non_field_errors'][0] == 'The fields email, project must make a unique set.')

  def test_can_reapply_to_project(self):
    """Assert that user can reapply to a project"""
    user = User.objects.create_user(email='owner_user@gmail.com', password="test_owner")
    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user)
    project.save()

    user = User.objects.create_user(email='apply_user@gmail.com', password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    # Apply
    response = client.post(reverse('project-apply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Successfully applied.')
    self.assertTrue(response.status_code == 200)

    project = Project.objects.get(slug="test-slug")
    self.assertTrue(project.applied_count == 1)

    # Unapply
    response = client.post(reverse('project-unapply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Successfully unapplied.')

    a = Apply.objects.last()
    self.assertTrue(a.canceled == True)
    self.assertTrue(a.canceled_date)

    project = Project.objects.get(slug="test-slug")
    self.assertTrue(project.applied_count == 0)

    # Reapply
    response = client.post(reverse('project-apply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Successfully applied.')
    self.assertTrue(response.status_code == 200)

    project = Project.objects.get(slug="test-slug")
    self.assertTrue(project.applied_count == 1)

    a = Apply.objects.last()
    self.assertTrue(a.canceled == False)
    self.assertTrue(a.canceled_date == None)

  def test_cant_unapply_if_not_apply_or_unauthenticated(self):
    """Assert that user can't unapply if not already applied or unauthenticated"""
    user = User.objects.create_user(email='owner_user@gmail.com', password="test_owner")
    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user)
    project.save()

    user = User.objects.create_user(email='apply_user@gmail.com', password="apply_user")

    client = APIClient()

    response = client.post(reverse('project-unapply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Authentication credentials were not provided.')
    self.assertTrue(response.status_code == 401)

    client.force_authenticate(user=user)
    response = client.post(reverse('project-unapply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'This is user is not applied to this project.')
    self.assertTrue(response.status_code == 400)

  def test_cant_apply_to_project_inexistent_project(self):
    """Assert that user can't apply to inexistent project"""
    user = User.objects.create_user(email='apply_user@gmail.com', password="apply_user")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse('project-apply', ['test-slug']), format='json')
    self.assertTrue(response.data['detail'] == 'Not found.')
    self.assertTrue(response.status_code == 404)


  def test_unauthenticated_user_cant_apply_to_project(self):
    """Assert that unauthenticated user cant apply to project"""
    user = User.objects.create_user(email='owner_user@gmail.com', password="test_owner")
    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse('project-apply', ['test-slug']), {'email': 'testemail@test.com'}, format='json')
    self.assertTrue(response.data['detail'] == 'Authentication credentials were not provided.')
    self.assertTrue(response.status_code == 401)


  @override_settings(OVP_USERS={'UNAUTHENTICATED_APPLY': True})
  def test_unauthenticated_user_can_apply_to_project(self):
    """Assert that unauthenticated user can apply to project if properly configured"""
    user = User.objects.create_user(email='owner_user@gmail.com', password="test_owner")
    project = Project(name="test project", slug="test-slug", details="abc", description="abc", owner=user)
    project.save()

    client = APIClient()

    response = client.post(reverse('project-apply', ['test-slug']), {'email': 'testemail@test.com'}, format='json')
    self.assertTrue(response.data['detail'] == 'Successfully applied.')
    self.assertTrue(response.status_code == 200)
