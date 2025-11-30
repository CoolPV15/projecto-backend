from django.db import models
"""
manager.py

This module defines custom model managers used to extend Django's default
queryset behavior. It includes the ProjectManager, responsible for handling
project creation logic with validation for required fields such as the owner.

Provides:
    - Safe creation of Project instances
    - Centralized validation for project-related database operations

Author: Pranav Singh
"""

class ProjectManager(models.Manager):
    """
    Custom manager for creating Project instances.

    Methods:
        create(owner, **extra_fields):
            Creates and saves a new project with the given owner and fields.

    Raises:
        ValueError: If the owner argument is missing or invalid.
    """

    def create(self, owner, **extra_fields):
        """
        Create a new project.

        Parameters:
            owner (User): The user who owns the project. Required.
            **extra_fields: Additional fields required by the Project model
                            such as projectname, description, etc.

        Returns:
            Project: The newly created project instance.

        Raises:
            ValueError: If owner is not provided.
        """
        if not owner:
            raise ValueError("User must be registered in the database")

        project = self.model(owner=owner, **extra_fields)
        project.save()
        return project