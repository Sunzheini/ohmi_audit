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

    # Bi-directional many-to-many relationship using explicit through model
    # Allows tracking additional metadata about the auditor's participation in audits
    related_auditors = models.ManyToManyField(
        'Auditor',
        related_name='audits',
        blank=True, # blank=True is appropriate for optional relationships
        through='AuditAuditor',  # doesn't auto create a table but uses the one specified
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


class AuditAuditor(models.Model):
    """
    Through model for many-to-many relationship between Audit and Auditor.
    """
    # One-to-many relationship
    audit = models.ForeignKey(
        Audit,
        on_delete=models.CASCADE,   # when Audit is deleted, delete related Auditors
        # on_delete=models.SET_NULL, null=True, # set null when Audit is deleted
        # on_delete=models.RESTRICT, # cannot delete if there is an Auditor attached
        related_name='auditor_assignments'
    )
    auditor = models.ForeignKey(
        Auditor,
        on_delete=models.CASCADE,
        related_name='audit_assignments'
    )

    assigned_date = models.DateField(
        auto_now_add=True,  # Automatically set to the date when the record is created
        blank=False,
        null=False,
    )

    is_lead_auditor = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text="Indicates if the auditor is the lead auditor for this audit",
    )

    def clean(self):
        """Ensure only one lead auditor per audit"""
        if self.is_lead_auditor:
            existing_leads = self.audit.auditor_assignments.filter(
                is_lead_auditor=True
            ).exclude(pk=self.pk)
            if existing_leads.exists():
                raise ValidationError("An audit can only have one lead auditor")

    def __str__(self):
        lead_status = " (Lead)" if self.is_lead_auditor else ""
        return f"{self.auditor.full_name} on {self.audit.name}{lead_status}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['audit', 'auditor'],
                name='unique_audit_auditor'
            )
        ]
        ordering = ['-assigned_date']  # Newest assignments first
        verbose_name = "Audit Assignment"
        verbose_name_plural = "Audit Assignments"
