"""
serializers.py

This module defines the serializers responsible for validating and
processing user-related data. It includes serializers for user
registration and for returning user profile details to the frontend.

Author: Pranav Singh
"""

from rest_framework import serializers
from .models import Users
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class UsersCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used for creating new user accounts.

    This serializer accepts user registration data from the frontend,
    validates the structure of the incoming fields, and delegates user
    creation to the custom `create_user()` method defined in the
    project's UserManager.

    Responsibilities:
        - Validate required registration fields.
        - Hash the user's password (handled inside UserManager).
        - Create and return a new Users instance.

    Meta:
        model (Users):
            Custom user model used for authentication.
        fields (tuple):
            Fields expected from the frontend, including:
                firstname, lastname, email, password, frontend, backend

    Methods:
        create(validated_data):
            Creates a User instance using Django’s custom user manager.

            Args:
                validated_data (dict):
                    Sanitized and validated data from the client.

            Returns:
                Users:
                    Newly created user object.
    """

    class Meta:
        model = Users
        fields = ("firstname", "lastname", "email", "password", "frontend", "backend")

    def create(self, validated_data):
        """
        Create and return a new user using the custom UserManager.

        Args:
            validated_data (dict):
                User details sent from the frontend.

        Returns:
            Users:
                Successfully created user object.
        """
        user = User.objects.create_user(
            firstname=validated_data["firstname"],
            lastname=validated_data["lastname"],
            email=validated_data["email"],
            password=validated_data["password"],
            frontend=validated_data["frontend"],
            backend=validated_data["backend"],
        )
        return user


class UsersSerializer(serializers.ModelSerializer):
    """
    Serializer for representing user details.

    This serializer is used to return non-sensitive user information
    (excluding password) back to the frontend.

    Meta:
        model (Users):
            Custom user model.
        fields (list[str]):
            firstname, lastname, email, frontend, backend
    """

    class Meta:
        model = Users
        fields = ["firstname", "lastname", "email", "frontend", "backend"]