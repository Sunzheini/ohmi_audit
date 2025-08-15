from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ohmi_audit.main_app.forms import AuditForm, SignUpForm, LoginForm
from ohmi_audit.main_app.models import Audit


class AuditFormTests(TestCase):
    def test_audit_form_valid_minimal(self):
        form = AuditForm(data={
            'name': 'My Audit',
            'description': 'desc',
            'date': timezone.now().date(),
            'is_active': True,
            'category': 'other',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_audit_form_invalid_missing_name(self):
        form = AuditForm(data={
            'name': '',
            'description': 'desc',
            'date': timezone.now().date(),
            'is_active': True,
            'category': 'other',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class SignUpFormTests(TestCase):
    def test_password_mismatch(self):
        form = SignUpForm(data={
            'username': 'user1',
            'email': 'user1@example.com',
            'first_name': 'User',
            'last_name': 'One',
            'password1': 'password123',
            'password2': 'password456',
        })
        self.assertFalse(form.is_valid())
        # HTML escapes apostrophes in error output
        self.assertIn("Passwords don&#x27;t match", str(form.errors))

    def test_successful_signup_creates_user(self):
        form = SignUpForm(data={
            'username': 'user2',
            'email': 'user2@example.com',
            'first_name': 'User',
            'last_name': 'Two',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        # Password is hashed
        self.assertTrue(user.check_password('password123'))


class LoginFormTests(TestCase):
    def test_login_form_has_custom_label(self):
        form = LoginForm()
        self.assertEqual(form.fields['username'].label, 'Username or Email')
