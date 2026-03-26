import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.common_models_data import CustomModelData
from ohmi_audit.main_app.models import *


class BaseModelTest:
    """Contains common tests for all models inheriting from CustomModelBase"""

    def test_full_name_property(self):
        assert hasattr(self.instance, 'full_name')
        assert isinstance(self.instance.full_name, str)

    def test_get_display_name(self):
        display_name = self.instance.get_display_name()
        assert isinstance(display_name, str)
        assert len(display_name) > 0

    def test_str_representation(self):
        assert str(self.instance) == self.instance.get_display_name()

    def test_clean_invokes_validate_model(self):
        """Find a field to make invalid based on model"""
        invalid_field = getattr(self, 'invalid_field', None)
        if invalid_field:
            original_value = getattr(self.instance, invalid_field)
            setattr(self.instance, invalid_field, '')
            with pytest.raises(ValidationError):
                self.instance.clean()
            setattr(self.instance, invalid_field, original_value)

    def test_slug_generation_on_save(self):
        """Test slug generation on save"""
        self.instance.slug = ''
        self.instance.save()
        assert self.instance.slug
        assert self.instance.slug == f"{self.instance.id}-{self.instance.full_name.lower().replace(' ', '-')}"


@pytest.mark.django_db
class TestAuditModel(BaseModelTest):
    @pytest.fixture(autouse=True)
    def setup(self):
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
        assert audit.is_active

    def test_max_length_constraints(self):
        """Test field length validations"""
        # Name too long
        self.audit.name = 'A' * (CustomModelData.MAX_CHARFIELD_LENGTH + 1)
        with pytest.raises(ValidationError):
            self.audit.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        self.audit.validate_model()  # Should not raise

    def test_validate_model_raises_on_empty_name(self):
        """Test empty name validation"""
        self.audit.name = ""
        with pytest.raises(ValidationError) as exc_info:
            self.audit.validate_model()
        assert "cannot be empty" in str(exc_info.value)


@pytest.mark.django_db
class TestAuditorModel(BaseModelTest):
    @pytest.fixture(autouse=True)
    def setup(self):
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
        with pytest.raises(ValidationError):
            self.auditor.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        self.auditor.validate_model()  # Should not raise

    def test_validate_model_raises_on_missing_names(self):
        """Test name validation"""
        # Empty first name
        self.auditor.first_name = ""
        with pytest.raises(ValidationError) as exc_info:
            self.auditor.validate_model()
        assert "First and last names are required" in str(exc_info.value)

    def test_validate_model_raises_on_empty_email(self):
        """Test email validation"""
        self.auditor.email = ""
        with pytest.raises(ValidationError) as exc_info:
            self.auditor.validate_model()
        assert "Email is required" in str(exc_info.value)


@pytest.mark.django_db
class TestCustomerModel(BaseModelTest):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.valid_data = {
            'year': 2026,
            'BG_Vor_Nr': 'BG-001/24',
            'company_name_bg': 'Тест ООД',
            'company_name_en': 'TEST LTD',
            'company_id': 123456789,
            'VAT_number': 'BG123456789',
        }
        self.customer = Customer.objects.create(**self.valid_data)
        self.instance = self.customer
        self.invalid_field = 'BG_Vor_Nr'  # For base class test

    def test_max_length_constraints(self):
        """Test field length validations"""
        self.customer.BG_Vor_Nr = 'A' * (CustomModelData.MAX_CHARFIELD_LENGTH + 1)
        with pytest.raises(ValidationError):
            self.customer.full_clean()

    def test_validate_model_with_valid_data(self):
        """Test validation passes with correct data"""
        self.customer.validate_model()  # Should not raise

    def test_validate_model_raises_on_empty_BG_Vor_Nr(self):
        """Test BG_Vor_Nr validation"""
        self.customer.BG_Vor_Nr = ""
        with pytest.raises(ValidationError) as exc_info:
            self.customer.validate_model()
        assert "BG_Vor_Nr is required" in str(exc_info.value)
