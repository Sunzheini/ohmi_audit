from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from common.common_forms_data import *
from ohmi_audit.main_app.models import *

__all__ = ['AuditForm', 'SignUpForm', 'LoginForm']
UserModel = get_user_model()


class AuditForm(forms.ModelForm, ChangeLabelsMixin, FormWidgetStylesMixin):
    class Meta:
        model = Audit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_widget_styles()
        self.change_to_current_labels()

    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation logic here if needed
        return cleaned_data


class SignUpForm(forms.ModelForm, ChangeLabelsMixin, FormWidgetStylesMixin):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm, ChangeLabelsMixin, FormWidgetStylesMixin):
    username = forms.CharField(label="Username or Email")

    class Meta:
        model = UserModel
        fields = ['username', 'password']
