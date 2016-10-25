from django.conf.urls import url, include
from rest_framework import routers

from ovp_projects import views

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectResourceViewSet, 'project')

urlpatterns = [
  url(r'^', include(router.urls)),
]
