"""
Serializers for handling project creation, project display, join requests,
member assignments, and rejected requests. These serializers validate user input,
perform custom object creation, and expose structured API representations.

Author: Pranav Singh
"""

from rest_framework import serializers
from .models import ProjectLead, ProjectRequest, ProjectMembers, ProjectRequestRejected
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectLeadCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating new projects.

    Extra Fields:
        email (str, write_only): Email of the user creating the project.

    Validates:
        - Whether the user with the given email exists.

    Creates:
        A new ProjectLead instance associated with the authenticated user.
    """

    email = serializers.EmailField(write_only=True)

    class Meta:
        model = ProjectLead
        fields = ["email", "projectname", "description", "frontend", "backend"]

    def create(self, validated_data):
        """
        Create a new project associated with a given user.

        Parameters:
            validated_data (dict): Validated project data.

        Returns:
            ProjectLead: Newly created project.

        Raises:
            ValidationError: If the user email does not match any user.
        """
        email = validated_data.pop("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist"})

        validated_data["owner"] = user

        project = ProjectLead.objects.create(
            owner=validated_data["owner"],
            projectname=validated_data["projectname"],
            description=validated_data["description"],
            frontend=validated_data["frontend"],
            backend=validated_data["backend"],
        )

        return project


class ProjectLeadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer used after a project is created.

    Includes:
        - email of project owner (readonly).
        - basic project details.
    """

    email = serializers.EmailField(read_only=True)

    class Meta:
        model = ProjectLead
        fields = ["email", "projectname", "description", "frontend", "backend"]


class ProjectDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer used for listing public project information.

    Adds:
        owner_email (str): Owner's email.
        fname (str): First name of owner.
        lname (str): Last name of owner.
    """

    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    fname = serializers.CharField(source="owner.firstname", read_only=True)
    lname = serializers.CharField(source="owner.lastname", read_only=True)

    class Meta:
        model = ProjectLead
        fields = [
            "owner_email",
            "fname",
            "lname",
            "projectname",
            "description",
            "frontend",
            "backend",
        ]


class ProjectRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used for submitting a project join request.

    Write-only Inputs:
        owner_email (str): Project owner's email.
        projectname (str): Name of the project user wants to join.
        member_email (str): Requesting user's email.

    Creates:
        A ProjectRequest record.

    Validates:
        - owner exists
        - member exists
        - project exists under owner
    """

    owner_email = serializers.EmailField(write_only=True)
    projectname = serializers.CharField(write_only=True)
    member_email = serializers.EmailField(write_only=True)

    class Meta:
        model = ProjectRequest
        fields = ["owner_email", "projectname", "member_email", "message"]

    def create(self, validated_data):
        """
        Create a new join request for a project.

        Parameters:
            validated_data (dict): Contains owner_email, projectname,
                                   member_email, and message.

        Returns:
            ProjectRequest: Newly created request object.

        Raises:
            ValidationError: For invalid owner, member, or project.
        """
        owner_email = validated_data.pop("owner_email")
        projectname = validated_data.pop("projectname")
        member_email = validated_data.pop("member_email")

        message = validated_data.get("message", "I am interested in joining this project")

        # Validate owner
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"owner_email": "Owner with this email does not exist."})

        # Validate member
        try:
            member = User.objects.get(email=member_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"member_email": "Member with this email does not exist."})

        # Validate project
        try:
            project = ProjectLead.objects.filter(owner=owner).get(projectname=projectname)
        except ProjectLead.DoesNotExist:
            raise serializers.ValidationError({"projectname": "This project does not exist."})

        # Create request
        new_request = ProjectRequest.objects.create(
            project=project,
            member=member,
            message=message,
        )

        return new_request


class ProjectRequestSerializer(serializers.ModelSerializer):
    """
    Serializer used for listing join requests received by the project owner.

    Read-only fields:
        id (int)
        email (str): Member's email.
        fname (str): First name.
        lname (str): Last name.
        message (str)
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(source="member.email", read_only=True)
    fname = serializers.CharField(source="member.firstname", read_only=True)
    lname = serializers.CharField(source="member.lastname", read_only=True)
    message = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectRequest
        fields = ["id", "email", "fname", "lname", "message"]


class ProjectMemberCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a new accepted member to a project.

    Write-only Inputs:
        email (str): Member email.
        owner (str): Owner email.
        projectname (str): Name of project.

    Creates:
        ProjectMembers entry.
    """

    email = serializers.EmailField(write_only=True)
    projectname = serializers.CharField(write_only=True)
    owner = serializers.EmailField(write_only=True)

    class Meta:
        model = ProjectMembers
        fields = ["email", "owner", "projectname","message"]

    def create(self, validated_data):
        """
        Add a user to a project's members list.

        Validates:
            - owner exists
            - member exists
            - project exists (owned by owner)

        Returns:
            ProjectMembers: newly added member record
        """
        owner_email = validated_data.pop("owner")
        member_email = validated_data.pop("email")
        projectname = validated_data.pop("projectname")

        # Validate owner
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"owner": "Owner with this email does not exist"})

        # Validate member
        try:
            member = User.objects.get(email=member_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"member": "Member with this email does not exist"})

        # Validate project
        try:
            project = ProjectLead.objects.filter(owner=owner).get(projectname=projectname)
        except ProjectLead.DoesNotExist:
            raise serializers.ValidationError({"project": "This project does not exist"})

        new_joinee = ProjectMembers.objects.create(
            project=project,
            member=member,
            message=validated_data["message"]
        )

        return new_joinee


class ProjectRejectedCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for storing rejected project join requests.

    Write-only Inputs:
        email (str): Member email.
        owner (str): Owner email.
        projectname (str): Name of the project.

    Creates:
        ProjectRequestRejected entry.
    """

    email = serializers.EmailField(write_only=True)
    projectname = serializers.CharField(write_only=True)
    owner = serializers.EmailField(write_only=True)

    class Meta:
        model = ProjectRequestRejected
        fields = ["email", "owner", "projectname","message"]

    def create(self, validated_data):
        """
        Create a rejected request record.

        Validates:
            - owner exists
            - member exists
            - project exists

        Returns:
            ProjectRequestRejected: newly created rejection record
        """
        projectname = validated_data.pop("projectname")
        owner_email = validated_data.pop("owner")
        member_email = validated_data.pop("email")

        # Validate owner
        try:
            owner = User.objects.get(email=owner_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"owner": "Owner with this email does not exist"})

        # Validate member
        try:
            member = User.objects.get(email=member_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"member": "Member with this email does not exist"})

        # Validate project
        try:
            project = ProjectLead.objects.filter(owner=owner).get(projectname=projectname)
        except ProjectLead.DoesNotExist:
            raise serializers.ValidationError({"project": "This project does not exist"})

        new_reject = ProjectRequestRejected.objects.create(
            project=project,
            user=member,
            message=validated_data["message"]
        )

        return new_reject

class JoinedProjectsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying all projects joined by a user.

    Read-only Fields:
        projectname (str): Name of the joined project.
        description (str): Description of the project.
        owner_email (str): Email of the project owner.
        owner_fname (str): First name of the project owner.
        owner_lname (str): Last name of the project owner.

    Returns:
        Project details with owner information for joined projects.
    """

    projectname = serializers.CharField(source="project.projectname", read_only=True)
    description = serializers.CharField(source="project.description", read_only=True)
    owner_email = serializers.EmailField(source="project.owner.email", read_only=True)
    owner_fname = serializers.CharField(source="project.owner.firstname", read_only=True)
    owner_lname = serializers.CharField(source="project.owner.lastname", read_only=True)

    class Meta:
        model = ProjectMembers
        fields = ["projectname", "description", "owner_email", "owner_fname", "owner_lname"]

class ProjectMembersDescription(serializers.ModelSerializer):
    """
    Serializer for listing members of a project.

    Read-only Fields:
        member_email (str): Email of the project member.
        member_fname (str): First name of the project member.
        member_lname (str): Last name of the project member.

    Returns:
        Basic details of all members in a project.
    """

    member_email = serializers.CharField(source="member.email", read_only=True)
    member_fname = serializers.CharField(source="member.firstname", read_only=True)
    member_lname = serializers.CharField(source="member.lastname", read_only=True)

    class Meta:
        model = ProjectMembers
        fields = ["member_email", "member_fname", "member_lname"]



class PendingProjectRequests(serializers.ModelSerializer):
    """
    Serializer for displaying pending project join requests made by a user.

    Read-only Fields:
        projectname (str): Name of the requested project.
        description (str): Description of the project.
        message (str): Message sent by the user in the join request.
        owner_email (str): Email of the project owner.
        owner_fname (str): First name of the project owner.
        owner_lname (str): Last name of the project owner.

    Returns:
        Details of all pending project requests with project and owner info.
    """

    projectname = serializers.CharField(source="project.projectname", read_only=True)
    description = serializers.CharField(source="project.description", read_only=True)
    owner_email = serializers.EmailField(source="project.owner.email", read_only=True)
    owner_fname = serializers.CharField(source="project.owner.firstname", read_only=True)
    owner_lname = serializers.CharField(source="project.owner.lastname", read_only=True)

    class Meta:
        model = ProjectRequest
        fields = ["projectname", "description", "message", "owner_email", "owner_fname", "owner_lname"]