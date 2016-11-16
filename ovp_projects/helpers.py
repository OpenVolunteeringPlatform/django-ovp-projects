from django.conf import settings
from rest_framework import exceptions

def get_settings():
  return getattr(settings, "OVP_USERS", {})
