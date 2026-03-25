"""
Authentication views.
Contains Sign Up, Login, and Logout views.
"""
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from common.base_view import BaseView
from ohmi_audit.main_app.forms import SignUpForm, LoginForm


class SignUpView(BaseView):
    """User registration view."""
    
    def define_basic_elements(self):
        self.template_name = 'main_app/index.html'
        self.form_class = SignUpForm
        self.page_title = _('Sign Up')
        self.page_name = _('Create Account')

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Account created successfully! Welcome, %(first_name)s!') % {'first_name': user.first_name})
            return redirect('index')

        # If form is invalid, return the form with errors
        return render(request, self.template_name, self.get_context_data(form=form))


class LoginView(BaseView):
    """User login view with rate limiting."""
    
    def define_basic_elements(self):
        self.template_name = 'main_app/index.html'
        self.form_class = LoginForm
        self.page_title = _('Login')
        self.page_name = _('Login to Your Account')

    def post(self, request: HttpRequest):
        # Rate limiting with Redis
        ip_address = request.META.get('REMOTE_ADDR')
        cache_key = f"login_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            messages.error(request, _('Too many login attempts. Please try again later.'))
            return render(request, self.template_name, self.get_context_data())

        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            # Reset attempts on successful login
            cache.delete(cache_key)

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request,
                                 _('Welcome back, %(first_name)s!') % {
                                     'first_name': user.first_name
                                 }
                                 )
                return redirect('index')
        else:
            # Increment failed attempts
            cache.set(cache_key, attempts + 1, timeout=300)  # 5 minute window
            messages.error(request, _('Invalid username or password'))

        return render(request, self.template_name, self.get_context_data(form=form))


class LogoutView(View):
    """User logout view."""
    
    @staticmethod
    def get(request):
        logout(request)
        messages.success(request, _('You have been successfully logged out.'))
        return redirect('index')

