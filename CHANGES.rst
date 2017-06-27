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

v1.0.2
-----------
* Include templates as package data

v1.0.3
-----------
* Add can_be_done_remotely to Work model

v1.0.4
-----------
* Add lat and lng to address on Project retrieval

v1.0.5
-----------
* Add organization to ProjectSearchSerializer

v1.0.6
-----------
* Add applies to ProjectRetrieveSerializer
* Add applied_count to ProjectRetrieveSerializer

v1.0.8
-----------
* Add max_applies_from_roles to Project

v1.0.9
-----------
* Allow members of organization to create/edit projects
* Implement manageable projects route

v1.0.10
-----------
* Upgrade ovp-organizations to 1.0.0

v1.0.11
-----------
* Add user to ApplyCreateSerializer

v1.0.12
-----------
* Upgrade ovp-organization to 1.0.3
* Add "user" to /projects/{slug}/applies/

v1.0.13
-----------
* Add /projects/{slug}/close/ route
* Fix errors with missing context on serializers
* Upgrade ovp-users to 1.0.16

v1.0.14
-----------
* Switch UserPublicRetrieveSerializer to UserProjectRetrieveSerializer in ProjectRetrieveSerializer

v1.0.15
-----------
* Fix user on project creation

v1.0.16
-----------
* Fix user on project creation(not really fixed before)

v1.0.17
-----------
* Add CSV renderer

v1.1.0
-----------
* Create OVP_PROJECTS.CAN_CREATE_PROJECTS_IN_ANY_ORGANIZATION setting

v1.1.1
-----------
* Add 'published' field to ProjectRetrieveSerializer

v1.1.2
-----------
* Fix missing context on ProjectResourceViewSet.applies

v1.1.3
-----------
* Update overrides and assertions so the module can be tested inside any django project

v1.1.4
-----------
[skipped release]

v1.1.5
-----------
* Remove many to many between job and jobdates and add fk on jobdate pointing to job

v1.1.6
-----------
* Implement admin panel
* Use GoogleAddressLatLngSerializer instead of GoogleAddressSerializer on ProjectSearchSerializer
* Add 'max_applies' and 'public_project' to Project model
* Project 'image' is now nullable

v1.1.7
-----------
* Add 'applied_count' to ProjectSearchSerializer
* Add 'minimum_age' field to Project model

v1.1.8
-----------
* Patch test_views.ApplyTestCase.test_unauthenticated_user_cant_apply_to_project to override settings

v1.1.9
-----------
* Upgrade dependencies

v1.1.10
-----------
* Implement Project.hidden_address field.
* Fix Project.max_applies_from_roles updating when creating/removing VolunteerRole
* Add missing tests

v1.2.0
-----------
* Add max_applies to ProjectSearchSerializer
* Apply.status is now a delimited choice field.
* Apply.status returned by API is not an "key" field anymore, but a readable string, so instead of getting "applied" and "unapplied" you might now get "Applied" and "Canceled".
* Introduced route /projects/{project.slug}/applies/{apply.id}/ which can be PATCHED by the project owner, organization owner or organization member to modify the status of an apply by a valid key choice.
* Apply and unapply routes are changed:
/projects/{slug}/apply/ => /projects/{slug}/applies/apply/
/projects/{slug}/unapply/ => /projects/{slug}/applies/unapply/

v1.2.1
-----------
* Fix test broken in last build

v1.2.2
-----------
* Add raw check on update_max_applies_from_roles signals

v1.2.3
-----------
* Set max_length for Apply.email to 190 so InnoDB stops complaining about index size with utf8mb4
* Fix hide_address decorator in case Project.hidden_address == False

v1.2.4
-----------
* Make 'canceled_date' and 'date' read-only on adm interface
* Add Crowdfunding Field and add public_project on serializers
* Add confirmed-volunteer and not-volunteer statuses to Apply
* Remove address_validate validtor on GoogleAddressSerializer
* Add admin notification on project created

v1.2.5
-----------
* Remove admin notification

v1.2.6
-----------
* Fix requirements

v1.2.7
-----------
* Upgrade ovp-core requirement

v1.2.8
-----------
* Add crowfunding field to Project model
* Add username, email and phone to Apply serializer
* Add ApplyUserRetrieveSerializer

v1.2.9
-----------
* Upgrade ovp-users
* Add Admin Email

v1.2.10
-----------
* Add causes and skills to project serializers
* Add ProjectOnOrganizationRetrieveSerializer
* Add disponibility on ProjectSearchSerializer

v1.2.11
-----------
* Add 'current_user_is_applied' to project retrieval
* Add pt_BR translations
* Add 'export_applied_users' route to export applied users info
* Add Organization and Owner in ProjectOnOrganizationRetrieveSerializer
* Use dynamic address on projects

v1.2.12
-----------
* Fix dependencies

v1.2.13[unreleased]
-----------
* Remove django.po from translation (now generated by deploy)
* Remove Project.address constraint
