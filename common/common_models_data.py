from abc import abstractmethod, ABC
from django.db import models


class CustomModelData:
    """
    Contains common data for models in the application.
    """
    MAX_CHARFIELD_LENGTH = 255
    MAX_FIRST_NAME_CHARFIELD_LENGTH = 100
    MAX_LAST_NAME_CHARFIELD_LENGTH = 100
    MAX_EMAIL_CHARFIELD_LENGTH = 254
    MAX_PHONE_CHARFIELD_LENGTH = 20

    # textfield
    MAX_TEXTFIELD_LENGTH = 1000


class CustomModelBase(models.Model, ABC):
    """
    Base model for all models in the application. Provides common fields
    and methods.

    Field names cannot have more than one underscore in a row and cannot
    end with an underscore
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def full_name(self):
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
    def get_display_name(self):
        """Return a display-friendly name for the model instance"""
        raise NotImplementedError("Subclasses must implement get_display_name()")

    @abstractmethod
    def validate_model(self):
        """Validate model data beyond standard field validation"""
        raise NotImplementedError("Subclasses must implement validate_model()")

    @abstractmethod
    def get_absolute_url(self):
        """Return URL for viewing the model instance"""
        raise NotImplementedError("Subclasses must implement get_absolute_url()")
