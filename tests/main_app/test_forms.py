import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from ohmi_audit.main_app.forms import AuditForm, SignUpForm, LoginForm
from ohmi_audit.main_app.models import Audit


@pytest.mark.django_db
class TestAuditForm:
    def test_audit_form_valid_minimal(self):
        form = AuditForm(data={
            'name': 'My Audit',
            'description': 'desc',
            'date': timezone.now().date(),
            'is_active': True,
            'category': 'other',
        })
        assert form.is_valid(), form.errors

    def test_audit_form_invalid_missing_name(self):
        form = AuditForm(data={
            'name': '',
            'description': 'desc',
            'date': timezone.now().date(),
            'is_active': True,
            'category': 'other',
        })
        assert not form.is_valid()
        assert 'name' in form.errors


@pytest.mark.django_db
class TestSignUpForm:
    def test_password_mismatch(self):
        form = SignUpForm(data={
            'username': 'user1',
            'email': 'user1@example.com',
            'first_name': 'User',
            'last_name': 'One',
            'password1': 'password123',
            'password2': 'password456',
        })
        assert not form.is_valid()
        # HTML escapes apostrophes in error output
        assert "Passwords don&#x27;t match" in str(form.errors)

    def test_successful_signup_creates_user(self):
        form = SignUpForm(data={
            'username': 'user2',
            'email': 'user2@example.com',
            'first_name': 'User',
            'last_name': 'Two',
            'password1': 'password123',
            'password2': 'password123',
        })
        assert form.is_valid(), form.errors
        user = form.save()
        assert user.pk is not None
        # Password is hashed
        assert user.check_password('password123')


class TestLoginForm:
    def test_login_form_has_custom_label(self):
        form = LoginForm()
        assert form.fields['username'].label == 'Username or Email'
