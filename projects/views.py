"""
Django REST Framework views for managing projects, join requests, team members,
and request rejections. These endpoints handle project creation, listing,
filtering, join request submission, approval, and rejection workflows.

Author: Pranav Singh
"""

from django.shortcuts import render
from rest_framework import viewsets
from .serializers import (
    ProjectLeadCreateSerializer,
    ProjectLeadSerializer,
    ProjectDisplaySerializer,
    ProjectRequestCreateSerializer,
    ProjectRequestSerializer,
    ProjectMemberCreateSerializer,
    ProjectRejectedCreateSerializer,
    JoinedProjectsSerializer,
    ProjectMembersDescription,
    PendingProjectRequests
)
from .models import ProjectLead, ProjectRequest, ProjectMembers, ProjectRequestRejected
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectLeadView(viewsets.ModelViewSet):
    """
    Handles CRUD operations for projects created by users (team leads).

    Endpoints:
        - POST /api/projectleads/ → create a new project.
        - GET /api/projectleads/?email=<email> → list projects owned by a user.
    """

    serializer_class = ProjectLeadCreateSerializer
    queryset = ProjectLead.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Create a new project owned by a user.

        Parameters:
            request (Request): Incoming HTTP request containing project data.

        Returns:
            Response: Created project data or validation errors.
        """
        data = request.data
        serializer = ProjectLeadCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project = serializer.create(serializer.validated_data)
        project = ProjectLeadSerializer(project)

        return Response(project.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """
        Filter projects created by a specific user using their email.

        Query Params:
            email (str): Email of the project owner.

        Returns:
            QuerySet of ProjectLead
        """
        queryset = ProjectLead.objects.all()
        email = self.request.query_params.get("email")

        if email:
            try:
                user = User.objects.get(email=email)
                queryset = queryset.filter(owner=user)
            except User.DoesNotExist:
                pass

        return queryset


class ProjectsDisplayView(viewsets.ModelViewSet):
    """
    Displays projects available to other users (not owned by them).

    Endpoints:
        GET /api/projects/?email=<email>&?frontend=<true/false>&?backend=<true/false>

    Supports filtering by:
        - Frontend requirement
        - Backend requirement
    """

    serializer_class = ProjectDisplaySerializer
    queryset = ProjectLead.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter projects based on user email and technology requirements.

        Query Params:
            email (str): Exclude projects owned by this user.
            frontend (str: "true"/"false"): Filter frontend-required.
            backend (str: "true"/"false"): Filter backend-required.

        Returns:
            QuerySet of ProjectLead
        """
        queryset = ProjectLead.objects.all()
        email = self.request.query_params.get("email")
        frontend = self.request.query_params.get("frontend")
        backend = self.request.query_params.get("backend")

        if email:
            try:
                user = User.objects.get(email=email)
                queryset = queryset.exclude(owner=user)
            except User.DoesNotExist:
                pass

            if frontend == "true" and backend == "true":
                pass
            elif frontend == "true":
                queryset = queryset.filter(frontend=True)
            elif backend == "true":
                queryset = queryset.filter(backend=True)
        
            projectsrequest = ProjectRequest.objects.all()
            projectsrequest = projectsrequest.filter(member=user).values_list("project",flat=True)

            projectsjoined = ProjectMembers.objects.all()
            projectsjoined = projectsjoined.filter(member=user).values_list("project",flat=True)

            # projectsreject = ProjectRequestRejected.objects.all()
            # projectsreject = projectsreject.filter(user=user).values_list("project",flat=True)

            queryset = queryset.exclude(id__in = projectsrequest)
            queryset = queryset.exclude(id__in = projectsjoined)
            # queryset = queryset.exclude(id__in = projectsreject)
        else:
            queryset = ProjectLead.objects.none()

        return queryset

class ProjectRequestView(viewsets.ModelViewSet):
    """
    Handles join request creation submitted by users.

    endpoint:
        POST /api/projectrequests/
    """

    serializer_class = ProjectRequestCreateSerializer
    queryset = ProjectRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Submit a join request for a project.

        Parameters:
            request (Request): User request containing join request details.

        Returns:
            Response: Created join request or validation errors.
        """
        data = request.data
        serializer = ProjectRequestCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_request = serializer.create(serializer.validated_data)
        new_request = ProjectRequestCreateSerializer(new_request)

        return Response(new_request.data, status=status.HTTP_201_CREATED)
    
class ProjectRequestDisplayView(viewsets.ModelViewSet):
    """
    Displays all join requests for a given project owned by a team lead.

    endpoint:
        GET /api/projectrequestsdisplay/?email=<leadEmail>&projectname=<name>
    """

    serializer_class = ProjectRequestSerializer
    queryset = ProjectRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Fetch join requests for a specific project owned by a user.

        Query Params:
            email (str): Owner email.
            projectname (str): Name of project.

        Returns:
            QuerySet of ProjectRequest
        """
        queryset = ProjectRequest.objects.all()
        email = self.request.query_params.get("email")
        projectname = self.request.query_params.get("projectname")

        if email and projectname:
            try:
                user = User.objects.get(email=email)
                project = ProjectLead.objects.get(owner=user, projectname=projectname)
                queryset = queryset.filter(project=project)
            except (User.DoesNotExist, ProjectLead.DoesNotExist):
                pass

        return queryset


class ProjectMembersView(viewsets.ModelViewSet):
    """
    Handles adding accepted members to projects.

    endpoint:
        POST /api/projectmembers/
    """

    serializer_class = ProjectMemberCreateSerializer
    queryset = ProjectMembers.objects.all()
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Add a member to a project after their request is approved.

        Parameters:
            request (Request): Contains owner email, applicant email, and project name.

        Returns:
            Response: Newly created ProjectMember record.
        """
        data = request.data
        serializer = ProjectMemberCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_member = serializer.create(serializer.validated_data)
        new_member = ProjectMemberCreateSerializer(new_member)

        return Response(new_member.data, status=status.HTTP_201_CREATED)


class ProjectRejectedView(viewsets.ModelViewSet):
    """
    Handles storing rejected join requests.

    endpoint:
        POST /api/projectreject/
    """

    serializer_class = ProjectRejectedCreateSerializer
    queryset = ProjectRequestRejected.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Log a rejected project join request.

        Parameters:
            request (Request): Includes owner email, applicant email, and project name.

        Returns:
            Response: Created rejection record.
        """
        data = request.data
        serializer = ProjectRejectedCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        rejected_request = serializer.create(serializer.validated_data)
        rejected_request = ProjectRejectedCreateSerializer(rejected_request)

        return Response(rejected_request.data, status=status.HTTP_201_CREATED)

class JoinedProjectDisplayView(viewsets.ModelViewSet):
    """
    Displays all projects joined by a specific user.

    endpoint:
        GET /api/joinedprojects/?email=<user_email>
    """

    serializer_class = JoinedProjectsSerializer
    queryset = ProjectMembers.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter joined projects based on email.

        Parameters:
            email (str): User email provided as a query parameter.

        Returns:
            QuerySet: Projects the user has joined.
        """
        queryset = ProjectMembers.objects.all()
        email = self.request.query_params.get("email")

        if email:
            try:
                user = User.objects.get(email=email)
                queryset = queryset.filter(member=user)
            except:
                pass

        return queryset


class ProjectMembersDisplayView(viewsets.ModelViewSet):
    """
    Returns all members of a specific project for a given owner.

    endpoint:
        GET /api/projectmembersdisplay/?email=<owner_email>&projectname=<project_name>
    """

    serializer_class = ProjectMembersDescription
    queryset = ProjectMembers.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get members of a project using owner email and project name.

        Parameters:
            email (str): Email of the project owner.
            projectname (str): Name of the project.

        Returns:
            QuerySet: List of members in the project.
        """
        queryset = ProjectMembers.objects.all()
        email = self.request.query_params.get("email")
        projectname = self.request.query_params.get("projectname")

        if email and projectname:
            try:
                user = User.objects.get(email=email)
                project = ProjectLead.objects.get(owner=user, projectname=projectname)
                queryset = ProjectMembers.objects.filter(project=project)
            except:
                pass

        return queryset

class PendingProjectsView(viewsets.ModelViewSet):
    """
    Displays pending project join requests for a user.

    endpoint:
        GET /api/pendingprojects/?email=<user_email>
    """

    serializer_class = PendingProjectRequests
    queryset = ProjectRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter pending join requests based on user email.

        Parameters:
            email (str): Email of the user.

        Returns:
            QuerySet: Pending project join requests for the user.
        """
        queryset = ProjectRequest.objects.all()
        email = self.request.query_params.get("email")

        if email:
            try:
                user = User.objects.get(email=email)
                queryset = ProjectRequest.objects.filter(member=user)
            except:
                pass

        return queryset
    
class ProjectCountView(viewsets.ModelViewSet):
    """
    Returns a summary count of projects for a user, including:
    - Number of projects created by the user
    - Number of projects the user has joined
    - Number of pending join requests

    Endpoint:
        GET /api/projectcount/?email=<user_email>
    """

    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Handle GET request to return project counts for a user.

        Parameters:
            request (HttpRequest): The incoming HTTP request containing query parameters.
            - email (str, query param): Email of the user for whom project counts are requested.

        Returns:
            Response: JSON object containing:
                - createdprojects (int): Total projects created by the user.
                - joinedprojects (int): Total projects the user has joined.
                - pendingrequests (int): Total pending join requests for the user.
        """
        email = self.request.query_params.get("email")

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, status=404
                )

            createdprojects = ProjectLead.objects.filter(owner=user).count()
            joinedprojects = ProjectMembers.objects.filter(member=user).count()
            pendingrequests = ProjectRequest.objects.filter(member=user).count()

            data = {
                "createdprojects": createdprojects,
                "joinedprojects": joinedprojects,
                "pendingrequests": pendingrequests
            }

            return Response(data)
        else:
            return Response(
                {"error": "Email query parameter is required"}, status=400
            )