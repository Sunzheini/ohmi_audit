from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from common.common_models_data import *


__all__ = ['Audit', 'Auditor', 'Customer']


class Audit(CustomModelBase):
    """
    Represents an audit record in the system.
    """
    name = models.CharField(max_length=CustomModelData.MAX_CHARFIELD_LENGTH)
    description = models.TextField(max_length=CustomModelData.MAX_TEXTFIELD_LENGTH)
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self) -> str:
        return self.name

    def get_display_name(self) -> str:
        return f"Audit: {self.name}"

    def validate_model(self) -> None:
        if not self.name.strip():
            raise ValidationError("Audit name cannot be empty")

    def get_absolute_url(self) -> str:
        return reverse('audit-detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.name


class Auditor(CustomModelBase):
    """
    Represents an auditor in the system.
    """
    first_name = models.CharField(max_length=CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH)
    last_name = models.CharField(max_length=CustomModelData.MAX_LAST_NAME_CHARFIELD_LENGTH)
    email = models.EmailField(max_length=CustomModelData.MAX_EMAIL_CHARFIELD_LENGTH)
    phone = models.CharField(max_length=CustomModelData.MAX_PHONE_CHARFIELD_LENGTH)

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def get_display_name(self) -> str:
        return f"Auditor: {self.full_name}"

    def validate_model(self) -> None:
        if not self.first_name.strip() or not self.last_name.strip():
            raise ValidationError("First and last names are required")
        if not self.email.strip():
            raise ValidationError("Email is required")

    def get_absolute_url(self) -> str:
        return reverse('auditor-detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.full_name


class Customer(CustomModelBase):
    """
    Represents a customer in the system.
    """
    first_name = models.CharField(max_length=CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH)
    last_name = models.CharField(max_length=CustomModelData.MAX_LAST_NAME_CHARFIELD_LENGTH)
    address = models.TextField(max_length=CustomModelData.MAX_TEXTFIELD_LENGTH)
    phone = models.CharField(max_length=CustomModelData.MAX_PHONE_CHARFIELD_LENGTH)
    email = models.EmailField(max_length=CustomModelData.MAX_EMAIL_CHARFIELD_LENGTH)

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def get_display_name(self) -> str:
        return f"Customer: {self.full_name}"

    def validate_model(self) -> None:
        if not self.address.strip():
            raise ValidationError("Address is required")
        if not self.phone.strip():
            raise ValidationError("Phone number is required")

    def get_absolute_url(self) -> str:
        return reverse('customer-detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.full_name
