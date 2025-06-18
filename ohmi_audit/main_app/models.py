from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.core.validators import MaxLengthValidator

from common.common_models_data import *

__all__ = ['Audit', 'Auditor', 'Customer']


class Audit(CustomModelBase):
    """
    Represents an audit record in the system.
    """
    # blank is used to allow empty values in forms, null is used to allow NULL in the database
    name = models.CharField(
        max_length=CustomModelData.MAX_CHARFIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )
    # for TextField, max_length is not enforced by the database, so we use a validator
    description = models.TextField(
        validators=[MaxLengthValidator(CustomModelData.MAX_TEXTFIELD_DESCRIPTION_LENGTH)],
        blank=True,
        null=False,
    )
    date = models.DateField(
        blank=False,
        null=False,
    )
    is_active = models.BooleanField(
        default=True,
        blank=False,
        null=False,
    )
    category = models.CharField(
        max_length=CustomModelData.MAX_CHARFIELD_LENGTH,
        choices=CustomModelData.AUDIT_CATEGORY_CHOICES,
        default='other',
        blank=True,  # Allow form to skip (will use default)
        null=False,
    )

    class Meta:
        verbose_name = "Audit"
        verbose_name_plural = "Audits"
        ordering = ['id']

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
    first_name = models.CharField(
        max_length=CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        max_length=CustomModelData.MAX_LAST_NAME_CHARFIELD_LENGTH,
        blank=False,
        null=False,
    )
    # max_length is 254 by default
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )
    phone = models.CharField(
        max_length=CustomModelData.MAX_PHONE_CHARFIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Auditor"
        verbose_name_plural = "Auditors"
        ordering = ['id']

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
    first_name = models.CharField(
        max_length=CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        max_length=CustomModelData.MAX_LAST_NAME_CHARFIELD_LENGTH,
        blank=False,
        null=False,
    )
    # for TextField, max_length is not enforced by the database, so we use a validator
    address = models.TextField(
        validators=[MaxLengthValidator(CustomModelData.MAX_TEXTFIELD_ADDRESS_LENGTH)],
        blank=False,
        null=False,
    )
    phone = models.CharField(
        max_length=CustomModelData.MAX_PHONE_CHARFIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['id']

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
