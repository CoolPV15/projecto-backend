"""
models.py

This module defines the custom Users model used for authentication and
authorization inside the application. It extends Django's AbstractBaseUser
and PermissionsMixin to provide complete control over user attributes,
login fields, and permission logic.

Author: Pranav Singh
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .manager import UserManager


class Users(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that replaces Django's default User.

    This model uses email instead of username for user authentication.
    It also stores additional profile fields such as first name,
    last name, and skill preferences (frontend/backend).

    Inherits:
        AbstractBaseUser:
            Provides core authentication fields such as password and last_login.
        PermissionsMixin:
            Adds fields and methods to support Django's permissions framework
            (groups, permissions, superuser status).

    Attributes:
        email (EmailField):
            Primary identifier for login. Must be unique.
        firstname (CharField):
            User's first name.
        lastname (CharField):
            User's last name.
        frontend (BooleanField):
            Indicates whether the user prefers frontend development.
        backend (BooleanField):
            Indicates whether the user prefers backend development.
        is_active (BooleanField):
            Determines whether the account is active.
        is_staff (BooleanField):
            Determines whether the user can access Django admin.
        date_joined (DateTimeField):
            Timestamp of when the user registered.

    Class Attributes:
        USERNAME_FIELD (str):
            Defines which field is used for authentication. Here: "email".
        REQUIRED_FIELDS (list[str]):
            Additional fields required when creating a superuser.

    Manager:
        objects (UserManager):
            Custom manager responsible for creating users and superusers
            with proper validation.

    Methods:
        __str__():
            Returns the user's email as a string representation.
    """

    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    frontend = models.BooleanField(default=False)
    backend = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstname", "lastname"]

    objects = UserManager()

    def __str__(self):
        """Return the user's email for readable string representation."""
        return self.email