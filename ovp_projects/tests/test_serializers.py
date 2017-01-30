from django.test import TestCase
from django.test import RequestFactory

from ovp_projects.models import Project
from ovp_projects.serializers.project import ProjectRetrieveSerializer
from ovp_projects.serializers.project import ProjectSearchSerializer

from ovp_users.models import User
from ovp_core.models import GoogleAddress
from ovp_organizations.models import Organization

class HiddenAddressTestCase(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(email="test_user@gmail.com", password="test")
    self.second_user = User.objects.create_user(email="test_second_user@test.com", password="test")
    self.third_user = User.objects.create_user(email="test_third_user@test.com", password="test")

    organization = Organization(name="test", type=0, owner=self.user)
    organization.save()
    organization.members.add(self.second_user)

    address = GoogleAddress(typed_address="Rua. Teçaindá, 81")
    address.save()
    self.project = Project(name="test project", slug="test slug", details="abc", description="abc", owner=self.user, hidden_address=True, address=address, organization=organization)
    self.project.save()

    self.request = RequestFactory().get('/')


  def test_project_search_serializer_hides_address(self):
    """ Assert ProjectSearchSerializer hides adress if Project.hidden_address == True """
    self._assert_serializer_hides_address(ProjectSearchSerializer)

  def test_project_retrieve_serializer_hides_address(self):
    """ Assert ProjectRetrieveSerializer hides adress if Project.hidden_address == True """
    self._assert_serializer_hides_address(ProjectRetrieveSerializer)

  def _assert_serializer_hides_address(self, serializer_class):
    # Owner
    self.request.user = self.user
    serializer = serializer_class(self.project, context={"request": self.request})
    self.assertTrue(serializer.data["address"]["typed_address"] == "Rua. Teçaindá, 81")
    self.assertTrue(serializer.data["hidden_address"] == True)

    # Organization member
    self.request.user = self.second_user
    serializer = serializer_class(self.project, context={"request": self.request})
    self.assertTrue(serializer.data["address"]["typed_address"] == "Rua. Teçaindá, 81")
    self.assertTrue(serializer.data["hidden_address"] == True)

    # Non member
    self.request.user = self.third_user
    serializer = serializer_class(self.project, context={"request": self.request})
    self.assertTrue(serializer.data["address"] == None)
    self.assertTrue(serializer.data["hidden_address"] == True)
