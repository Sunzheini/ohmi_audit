"""
Single conftest.py for all pytest configuration and fixtures
"""
import pytest
import django
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model


# Configure Django settings for pytest
def pytest_configure(config):
    """Configure Django for pytest"""
    if not settings.configured:
        django.setup()


# ============================================================================
# General Fixtures
# ============================================================================

@pytest.fixture
def clear_cache():
    """Clear Django cache before/after test"""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    """Provide REST Framework API client for tests"""
    from rest_framework.test import APIClient
    return APIClient()


# ============================================================================
# User Fixtures
# ============================================================================

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Provide an authenticated Django test client"""
    client.login(username='testuser', password='testpass123')
    return client


# ============================================================================
# Model Fixtures (main_app)
# ============================================================================

@pytest.fixture
def audit(db):
    """Create a test audit"""
    from ohmi_audit.main_app.models import Audit
    return Audit.objects.create(
        name='Test Audit',
        description='Test audit description',
        date=timezone.now().date(),
        is_active=True
    )


@pytest.fixture
def auditor(db):
    """Create a test auditor"""
    from ohmi_audit.main_app.models import Auditor
    return Auditor.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='+1234567890'
    )


@pytest.fixture
def customer(db):
    """Create a test customer"""
    from ohmi_audit.main_app.models import Customer
    return Customer.objects.create(
        year=2026,
        BG_Vor_Nr='BG-001/24',
        company_name_bg='Тест ООД',
        company_name_en='TEST LTD',
        company_id=123456789,
        VAT_number='BG123456789',
    )

