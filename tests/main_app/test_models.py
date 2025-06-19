from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.common_models_data import CustomModelData
import unittest
from ohmi_audit.main_app.models import *


class BaseModelTest:
    """Contains common tests for all models inheriting from CustomModelBase"""

    def test_full_name_property(self):
        self.assertTrue(hasattr(self.instance, 'full_name'))
        self.assertIsInstance(self.instance.full_name, str)

    def test_get_display_name(self):
        display_name = self.instance.get_display_name()
        self.assertIsInstance(display_name, str)
        self.assertTrue(len(display_name) > 0)

    def test_str_representation(self):
        self.assertEqual(str(self.instance), self.instance.get_display_name())

    def test_clean_invokes_validate_model(self):
        """Find a field to make invalid based on model"""
        invalid_field = getattr(self, 'invalid_field', None)
        if invalid_field:
            original_value = getattr(self.instance, invalid_field)
            setattr(self.instance, invalid_field, '')
            with self.assertRaises(ValidationError):
                self.instance.clean()
            setattr(self.instance, invalid_field, original_value)

    def test_slug_generation_on_save(self):
        """Test slug generation on save"""
        self.instance.slug = ''
        self.instance.save()
        self.assertTrue(self.instance.slug)
        self.assertEqual(self.instance.slug, f"{self.instance.id}-{self.instance.full_name.lower().replace(' ', '-')}")



class AuditModelTest(BaseModelTest, TestCase):
    def setUp(self):
        self.valid_data = {
            'name': "Test Audit",
            'description': "This is a test audit.",
            'date': timezone.now().date(),
            'is_active': True
        }
        self.audit = Audit.objects.create(**self.valid_data)
        self.instance = self.audit
        self.invalid_field = 'name'  # For base class test

    def test_default_is_active(self):
        """Test is_active default value when not specified"""
        audit = Audit.objects.create(
            name="Default Test",
            description="Test",
            date=timezone.now().date()
        )
        self.assertTrue(audit.is_active)

    def test_max_length_constraints(self):
        """Test field length validations"""
        # Name too long
        self.audit.name = 'A' * (CustomModelData.MAX_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.audit.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        try:
            self.audit.validate_model()
        except ValidationError:
            self.fail("validate_model() raised ValidationError unexpectedly!")

    def test_validate_model_raises_on_empty_name(self):
        """Test empty name validation"""
        self.audit.name = ""
        with self.assertRaises(ValidationError) as cm:
            self.audit.validate_model()
        self.assertIn("cannot be empty", str(cm.exception))


class AuditorModelTest(BaseModelTest, TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        self.auditor = Auditor.objects.create(**self.valid_data)
        self.instance = self.auditor
        self.invalid_field = 'email'  # For base class test

    def test_max_length_constraints(self):
        """Test field length validations"""
        # First name too long
        self.auditor.first_name = 'A' * (CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.auditor.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        try:
            self.auditor.validate_model()
        except ValidationError:
            self.fail("validate_model() raised ValidationError unexpectedly!")

    def test_validate_model_raises_on_missing_names(self):
        """Test name validation"""
        # Empty first name
        self.auditor.first_name = ""
        with self.assertRaises(ValidationError) as cm:
            self.auditor.validate_model()
        self.assertIn("First and last names are required", str(cm.exception))

    def test_validate_model_raises_on_empty_email(self):
        """Test email validation"""
        self.auditor.email = ""
        with self.assertRaises(ValidationError) as cm:
            self.auditor.validate_model()
        self.assertIn("Email is required", str(cm.exception))


class CustomerModelTest(BaseModelTest, TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'address': '123 Main St',
            'phone': '+1987654321',
            'email': 'alice@example.com'
        }
        self.customer = Customer.objects.create(**self.valid_data)
        self.instance = self.customer
        self.invalid_field = 'phone'  # For base class test

    def test_max_length_constraints(self):
        """Test field length validations"""
        # First name too long
        self.customer.first_name = 'A' * (CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.customer.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        try:
            self.customer.validate_model()
        except ValidationError:
            self.fail("validate_model() raised ValidationError unexpectedly!")

    def test_validate_model_raises_on_empty_address(self):
        """Test address validation"""
        self.customer.address = ""
        with self.assertRaises(ValidationError) as cm:
            self.customer.validate_model()
        self.assertIn("Address is required", str(cm.exception))


if __name__ == '__main__':
    unittest.main()