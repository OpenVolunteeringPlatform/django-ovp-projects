from ovp_core.emails import BaseMail

class ProjectMail(BaseMail):
  """
  This class is responsible for firing emails for Project related actions
  """
  def __init__(self, project, async_mail=None):
    super(ProjectMail, self).__init__(project.owner.email, async_mail)

  def sendProjectCreated(self, context={}):
    """
    Sent when user creates a project
    """
    return self.sendEmail('projectCreated', 'Project created', context)


  def sendProjectPublished(self, context):
    """
    Sent when project is published
    """
    return self.sendEmail('projectPublished', 'Project published', context)


  def sendProjectClosed(self, context):
    """
    Sent when project gets closed
    """
    return self.sendEmail('projectClosed', 'Project closed', context)



class ApplyMail(BaseMail):
  """
  This class is responsible for firing emails for apply related actions
  """
  def __init__(self, apply, async_mail=None):
    self.apply = apply
    self.async = async_mail
    super(ApplyMail, self).__init__(apply.email, async_mail)

  def sendAppliedToVolunteer(self, context={}):
    """
    Sent to user when he applies to a project
    """
    return self.sendEmail('volunteerApplied-ToVolunteer', 'Applied to project', context)


  def sendAppliedToOwner(self, context={}):
    """
    Sent to project owner when user applies to a project
    """
    super(ApplyMail, self).__init__(self.apply.project.owner.email, self.async)
    return self.sendEmail('volunteerApplied-ToOwner', 'New volunteer', context)


  def sendUnappliedToVolunteer(self, context={}):
    """
    Sent to user when he unapplies from a project
    """
    return self.sendEmail('volunteerUnapplied-ToVolunteer', 'Unapplied from project', context)


  def sendUnappliedToOwner(self, context={}):
    """
    Sent to project owner when user unapplies from a project
    """
    super(ApplyMail, self).__init__(self.apply.project.owner.email, self.async)
    return self.sendEmail('volunteerUnapplied-ToOwner', 'Volunteer unapplied from project', context)
