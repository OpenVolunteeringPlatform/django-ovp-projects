===========
Change log
===========

v0.1.0
-----------
* Start project
* Update README
* Add initial migration
* Add codeship and codecov badge

v0.1.1
-----------
* Include version badge to README.rst
* Remove unneeded text from README.rst
* Add ovp_uploads as dependency
* Add image to project model
* Drop distutils in favor of setuptools

v0.1.1b
-----------
* Add .egg-info to gitignore

v0.1.2
-----------
* Return serialized image
* Use correct user on project creation

v0.1.3
-----------
* Add organization to project model

v1.0.0
-----------
* Allows project.image to be nullable while still being required(fix issue with mysql)
* Allows project.organization to be nullable while still being required(fix issue with mysql)
* Move models.py to separate files inside models/
* Update datetime module to django timezone module on models
* Remove id, details and organization from ProjectSearchSerializer and create ProjectRetrieveSerializer with such information
* Add ovp-users as dependency
* Rename Role model to VolunteerRole
* Implement Project.get_phone() and .get_email()
* Implement project edit route
* Implement roles, disponibility(work and job)
* Add permissions to create and edit project
* Upgrade to drf 3.5.3
* Create applies routes (create, remove and list)
* Add applied_count field to project
* Add project creation, publishing and closing, applying and unapplying 
* Automatic slug on project creation
* Add close_finished_projects command
* Release as stable (YAY \o/)

v1.0.1
-----------
* Fix mistyped template name
* Include test for project update
