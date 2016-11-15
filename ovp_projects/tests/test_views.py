# test project resource edit
# test project resource delete
# test is part of organization to create, edit
# test must be owner to delete project

from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp_projects.models import Project
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
