# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ovp-projects',
    version='1.2.9',
    author=u'Atados',
    author_email='arroyo@atados.com.br',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/OpenVolunteeringPlatform/django-ovp-projects',
    download_url = 'https://github.com/OpenVolunteeringPlatform/django-ovp-projects/tarball/1.2.9',
    license='AGPL',
    description='This module has core functionality for' + \
                ' ovp projects, such as creation, editing' + \
                ' and retrieving.',
    long_description=open('README.rst', encoding='utf-8').read(),
    zip_safe=False,
    install_requires = [
      'Django>=1.10.1,<1.11.0',
      'djangorestframework>=3.5.0,<3.6.0',
      'djangorestframework-jwt>=1.8.0,<2.0.0',
      'python-dateutil>=2.5.3,<2.7.0',
      'codecov>=2.0.5,<2.1.0',
      'coverage>=4.2,<4.4.0',
      'ovp-users>=1.1.6,<2.0.0',
      'ovp-core>=1.2.4,<2.0.0',
      'ovp-uploads>=1.0.0,<2.0.0',
      'ovp-organizations>=1.0.0,<2.0.0',
    ],
    dependency_links = [
      'git+https://github.com/alanjds/drf-nested-routers.git@0438289'
    ]
)
