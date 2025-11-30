"""
user_manager.py

Custom user manager for handling creation of regular users and superusers
within the authentication system. Extends Django's BaseUserManager to enforce
email-based authentication and ensure proper permission settings for admin
accounts.

Author: Pranav Singh
"""

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """
    Custom manager for handling user and superuser creation.

    Methods:
        create_user(email, password, **extra_fields):
            Creates and returns a standard user with a validated email.

        create_superuser(email, password, **extra_fields):
            Creates a superuser with mandatory admin privileges.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and return a regular authenticated user.

        Parameters:
            email (str): User's email address. Required.
            password (str): Plain-text password to be hashed before saving.
            **extra_fields: Additional model fields such as firstname,
                            lastname, skills, etc.

        Raises:
            ValueError: If no email is provided.

        Returns:
            User: Newly created user instance.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser with elevated permissions.

        Ensures:
            - is_staff = True
            - is_superuser = True
            - is_active = True

        Parameters:
            email (str): Admin's email address.
            password (str): Admin's password.
            **extra_fields: Additional fields for the superuser record.

        Raises:
            ValueError: If required permissions are not correctly set.

        Returns:
            User: Newly created superuser instance.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(email, password, **extra_fields)