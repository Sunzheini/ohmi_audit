from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.common_models_data import CustomModelData
import unittest
from ohmi_audit.main_app.models import *


class AuditModelTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': "Test Audit",
            'description': "This is a test audit.",
            'date': timezone.now().date(),
            'is_active': True
        }
        self.audit = Audit.objects.create(**self.valid_data)

    # -------- Fields' Tests --------
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

    # -------- Methods' Tests --------
    def test_full_name(self):
        """Test that full_name property returns correct value"""
        self.assertEqual(self.audit.full_name, "Test Audit")

    def test_get_display_name(self):
        """Test display name formatting"""
        self.assertEqual(
            self.audit.get_display_name(),
            "Audit: Test Audit"
        )
        # Test with changed name
        self.audit.name = "New Name"
        self.assertEqual(
            self.audit.get_display_name(),
            "Audit: New Name"
        )

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

    def test_clean_invokes_validate_model(self):
        """Test Django's clean() calls our validate_model()"""
        self.audit.name = ""
        with self.assertRaises(ValidationError):
            self.audit.clean()  # Should call validate_model()

    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.audit), "Test Audit")
        self.audit.name = "New Name"
        self.assertEqual(str(self.audit), "New Name")


class AuditorModelTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        self.auditor = Auditor.objects.create(**self.valid_data)

    # -------- Fields' Tests --------
    def test_max_length_constraints(self):
        """Test field length validations"""
        # First name too long
        self.auditor.first_name = 'A' * (CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.auditor.full_clean()

        # Email too long
        self.auditor.first_name = 'Valid'
        self.auditor.email = 'a' * (CustomModelData.MAX_EMAIL_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.auditor.full_clean()

    # -------- Methods' Tests --------
    def test_full_name_property(self):
        """Test full_name property concatenation"""
        self.assertEqual(self.auditor.full_name, "John Doe")
        self.auditor.first_name = "Jane"
        self.assertEqual(self.auditor.full_name, "Jane Doe")

    def test_get_display_name(self):
        """Test display name formatting"""
        self.assertEqual(
            self.auditor.get_display_name(),
            "Auditor: John Doe"
        )
        self.auditor.last_name = "Smith"
        self.assertEqual(
            self.auditor.get_display_name(),
            "Auditor: John Smith"
        )

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

        # Empty last name
        self.auditor.first_name = "John"
        self.auditor.last_name = ""
        with self.assertRaises(ValidationError) as cm:
            self.auditor.validate_model()
        self.assertIn("First and last names are required", str(cm.exception))

    def test_validate_model_raises_on_empty_email(self):
        """Test email validation"""
        self.auditor.email = ""
        with self.assertRaises(ValidationError) as cm:
            self.auditor.validate_model()
        self.assertIn("Email is required", str(cm.exception))

    def test_clean_invokes_validate_model(self):
        """Test Django's clean() calls our validate_model()"""
        self.auditor.email = ""
        with self.assertRaises(ValidationError):
            self.auditor.clean()

    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.auditor), "John Doe")
        self.auditor.first_name = "Jane"
        self.assertEqual(str(self.auditor), "Jane Doe")


class CustomerModelTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'address': '123 Main St',
            'phone': '+1987654321',
            'email': 'alice@example.com'
        }
        self.customer = Customer.objects.create(**self.valid_data)

    # -------- Fields' Tests --------
    def test_max_length_constraints(self):
        """Test field length validations"""
        # First name too long
        self.customer.first_name = 'A' * (CustomModelData.MAX_FIRST_NAME_CHARFIELD_LENGTH + 1)
        with self.assertRaises(ValidationError):
            self.customer.full_clean()


    # -------- Methods' Tests --------
    def test_full_name_property(self):
        """Test full_name property concatenation"""
        self.assertEqual(self.customer.full_name, "Alice Johnson")
        self.customer.last_name = "Smith"
        self.assertEqual(self.customer.full_name, "Alice Smith")

    def test_get_display_name(self):
        """Test display name formatting"""
        self.assertEqual(
            self.customer.get_display_name(),
            "Customer: Alice Johnson"
        )
        self.customer.first_name = "Bob"
        self.assertEqual(
            self.customer.get_display_name(),
            "Customer: Bob Johnson"
        )

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

    def test_validate_model_raises_on_empty_phone(self):
        """Test phone validation"""
        self.customer.phone = ""
        with self.assertRaises(ValidationError) as cm:
            self.customer.validate_model()
        self.assertIn("Phone number is required", str(cm.exception))

    def test_clean_invokes_validate_model(self):
        """Test Django's clean() calls our validate_model()"""
        self.customer.phone = ""
        with self.assertRaises(ValidationError):
            self.customer.clean()

    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.customer), "Alice Johnson")
        self.customer.last_name = "Williams"
        self.assertEqual(str(self.customer), "Alice Williams")


if __name__ == '__main__':
    unittest.main()
