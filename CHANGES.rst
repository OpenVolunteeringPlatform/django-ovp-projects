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

v0.1.4[unreleased]
-----------
* Allows project.image to be nullable while still being required(fix issue with mysql)

todo
* Assert user owns organization
* Implement job/work
* Project apply
* Email layouts
* Project editing/deleting
* Permission class to create/edit project(owner/member of nonprofit)
