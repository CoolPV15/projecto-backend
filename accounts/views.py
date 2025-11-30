""" 
views.py 

This module defines API views related to user authentication, registration, logout handling, 
and profile retrieval. It uses Django REST Framework (APIs, serializers, permissions) along 
with JWT-based authentication via SimpleJWT. 

Author: Pranav Singh 
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UsersCreateSerializer, UsersSerializer
from .models import Users
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeView(APIView):
    """
    Returns profile data of the authenticated user.

    Endpoints:
        - GET /api/home/ - retrieve basic logged-in user details.

    This endpoint requires a valid JWT access token and returns the user's
    basic profile information such as name, email, and skill preferences.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve authenticated user details.

        Parameters:
            request (Request): HTTP GET request with Authorization token.

        Returns:
            Response: JSON containing user details including firstname,
                      lastname, email, and tech roles.
        """
        user = request.user
        return Response({
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "frontend": user.frontend,
            "backend": user.backend,
        })


class RegistrationView(viewsets.ModelViewSet):
    """
    Handles user account registration.

    Endpoints:
        - POST /api/register/ - register a new user.

    This view validates incoming registration data using
    `UsersCreateSerializer` and creates a new user record upon success.
    """

    serializer_class = UsersCreateSerializer
    queryset = Users.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Register a new user.

        Parameters:
            request (Request): Incoming HTTP POST request containing
                               registration details.

        Returns:
            Response:
                - 201 Created with user data upon success.
                - 400 Bad Request with validation errors otherwise.
        """
        data = request.data
        serializer = UsersCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.create(serializer.validated_data)
        user = UsersSerializer(user)

        return Response(user.data, status=status.HTTP_201_CREATED)


class LogOutView(APIView):
    """
    Logs out a user by blacklisting their refresh token.

    Endpoints:
        - POST /api/logout/ - blacklist refresh token and logout user.

    Requires the client to send a valid refresh token. The token is then
    added to the blacklist so it cannot be reused to generate new access tokens.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Blacklist the provided refresh token.

        Parameters:
            request (Request): POST request containing 'refresh_token'.

        Returns:
            Response:
                - 205 Reset Content on success.
                - 400 Bad Request if the token is invalid or missing.
        """
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"Error": "Refresh Token Required"})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"Success": "Logged Out"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUserView(APIView):
    """
    Returns complete profile of the authenticated user.

    Endpoints:
        - GET /api/user/ - retrieve full serialized user profile.

    This endpoint provides all user information using `UsersSerializer`
    and requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return complete serialized user profile.

        Parameters:
            request (Request): HTTP GET request sent by authenticated user.

        Returns:
            Response: Serialized user information.
        """
        user = request.user
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)