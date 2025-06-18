from abc import abstractmethod, ABC, ABCMeta
from django.db import models

# define the __all__ variable to control what is imported when using 'from module import *'
__all__ = ['CustomModelData', 'CustomModelBase']


class CustomModelData:
    """
    Contains common data for models in the application.
    """
    MAX_CHARFIELD_LENGTH = 255
    MAX_FIRST_NAME_CHARFIELD_LENGTH = 100
    MAX_LAST_NAME_CHARFIELD_LENGTH = 100
    MAX_PHONE_CHARFIELD_LENGTH = 20

    MAX_TEXTFIELD_DESCRIPTION_LENGTH = 1000
    MAX_TEXTFIELD_ADDRESS_LENGTH = 500

    AUDIT_CATEGORY_CHOICES = (
        # On the left side, the value stored in the database, on the right side, the human-readable name
        ('compliance', 'Compliance'),
        ('information_security', 'Information Security'),
        ('health_and_safety', 'Health and Safety'),
        ('other', 'Other'),
    )


class CustomModelBase(models.Model):
    """
    Base model for all models in the application. Provides common fields
    and methods.

    Field names cannot have more than one underscore in a row and cannot
    end with an underscore
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def full_name(self) -> str:
        """For models that have name components"""
        raise NotImplementedError

    def clean(self):
        """
        Custom clean method to validate the model data.
        :return: None
        """
        super().clean()
        self.validate_model()  # Keep your custom validation

    @abstractmethod
    def get_display_name(self) -> str:
        """Return a display-friendly name for the model instance"""
        raise NotImplementedError("Subclasses must implement get_display_name()")

    @abstractmethod
    def validate_model(self):
        """Validate model data beyond standard field validation"""
        raise NotImplementedError("Subclasses must implement validate_model()")

    @abstractmethod
    def get_absolute_url(self) -> str:
        """Return URL for viewing the model instance"""
        raise NotImplementedError("Subclasses must implement get_absolute_url()")
