"""
models.py

This module defines all database models used for handling project creation,
project join requests, accepted members, and rejected join attempts within
the collaboration system.

Author: Pranav Singh
"""

from django.db import models
from django.conf import settings


class ProjectLead(models.Model):
    """
    Represents a project created by a user.

    Attributes:
        owner (ForeignKey):
            A reference to the user who owns/created the project.
            Deletes the project if the user is deleted.
        projectname (CharField):
            Name of the project (unique per user).
        description (CharField):
            Brief description about the purpose or details of the project.
        frontend (BooleanField):
            Indicates if the project requires frontend developers.
        backend (BooleanField):
            Indicates if the project requires backend developers.
        created_at (DateTimeField):
            Timestamp of when the project was created.

    Meta:
        unique_together:
            Ensures that each user cannot create multiple projects with
            the same name.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    projectname = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    frontend = models.BooleanField(default=False)
    backend = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("owner", "projectname"),)

    def __str__(self):
        return f"{self.projectname} ({self.owner.email})"


class ProjectRequest(models.Model):
    """
    Represents a request made by a user to join a project.

    Attributes:
        project (ForeignKey):
            The project the user is requesting to join.
        member (ForeignKey):
            The user who is sending the request.
        message (CharField):
            Optional message sent by the requester.

    Meta:
        unique_together:
            Ensures the same user cannot request to join the
            same project multiple times.
    """

    project = models.ForeignKey(
        ProjectLead,
        on_delete=models.CASCADE,
        related_name="project_lead"
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_member"
    )
    message = models.CharField(max_length=400, default="I am interested in joining this project")

    class Meta:
        unique_together = (("project", "member"),)

    def __str__(self):
        return f"Request by {self.member.email} for {self.project.projectname}"


class ProjectMembers(models.Model):
    """
    Represents a user who has been accepted into a project team.

    Attributes:
        project (ForeignKey):
            The project the member has joined.
        member (ForeignKey):
            The user who joined the project.
        message (CharField):
            Message attached when joining (default provided).
        joined_on (DateTimeField):
            Timestamp of joining.

    Meta:
        unique_together:
            Prevents the same user from being added to the same project twice.
    """

    project = models.ForeignKey(
        ProjectLead,
        on_delete=models.CASCADE,
        related_name="project_joined"
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_name"
    )
    message = models.CharField(max_length=400, default="I am interested in joining this project")
    joined_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "member"),)

    def __str__(self):
        return f"{self.member.email} joined {self.project.projectname}"


class ProjectRequestRejected(models.Model):
    """
    Represents a rejected project join request.

    Attributes:
        project (ForeignKey):
            The project for which the request was rejected.
        user (ForeignKey):
            The user whose request was rejected.
        message (CharField):
            Optional message attached to the rejected request (default provided).
        rejected_on (DateTimeField):
            Timestamp when the rejection occurred.

    Meta:
        unique_together:
            Ensures that a user cannot be marked rejected for the same
            project multiple times.
    """

    project = models.ForeignKey(
        ProjectLead,
        on_delete=models.CASCADE,
        related_name="project_rejected"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_name"
    )
    message = models.CharField(max_length=400, default="I am interested in joining this project")
    rejected_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "user"),)

    def __str__(self):
        return f"{self.user.email} rejected from {self.project.projectname}"