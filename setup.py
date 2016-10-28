# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ovp-projects',
    version='0.1.3',
    author=u'Atados',
    author_email='arroyo@atados.com.br',
    packages=find_packages(),
    url='https://github.com/OpenVolunteeringPlatform/django-ovp-projects',
    download_url = 'https://github.com/OpenVolunteeringPlatform/django-ovp-projects/tarball/0.1.3',
    license='AGPL',
    description='This module has core functionality for' + \
                ' ovp projects, such as creation, editing' + \
                ' and retrieving.',
    long_description=open('README.rst', encoding='utf-8').read(),
    zip_safe=False,
    install_requires = [
      'Django>=1.10.1,<1.11.0',
      'djangorestframework>=3.4.7,<3.5.0',
      'djangorestframework-jwt>=1.8.0,<1.9.0',
      'python-dateutil>=2.5.3,<2.6.0',
      'codecov>=2.0.5,<2.1.0',
      'coverage>=4.2,<4.3.0',
      'ovp-core>=0.1.4,<1.0.0',
      'ovp-uploads>=0.1.3,<1.0.0',
      'ovp-organizations>=0.1.1,<1.0.0',
    ]
)
