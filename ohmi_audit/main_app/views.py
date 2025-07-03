from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from ohmi_audit.main_app.forms import *
from ohmi_audit.main_app.models import Audit


# You can use the get_user_model() function to get the user model
UserModel = get_user_model()
all_users = list(UserModel.objects.all())
a = 1


class IndexView(LoginRequiredMixin, View):
    template_name = 'main_app\index.html'
    form_class = AuditForm
    page_title = 'Ohmi Audit Test'
    page_name = 'Welcome'

    # for the LoginRequiredMixin
    login_url = '/login/'  # Redirect to this URL if not logged in
    redirect_field_name = 'next'  # URL parameter to redirect after login

    def get_context_data(self, **kwargs):
        """Shared context for both GET and POST"""
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,

            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),     # Pass the form instance, not the class
            'data_for_content_container_wrapper_bottom': Audit.objects.all(),
        }
        return context

    # GET and POST are the only HTTP methods to use when dealing with forms in Django.
    def get(self, request: HttpRequest):
        """
        :param request: Even though `request` is technically WSGIRequest, you can type-hint it as
        HttpRequest for clarity.
        :return: HttpResponse rendering the index page through the render function. You can also
        return a simple HttpResponse with raw HTML content:
        `return HttpResponse("<h1>Welcome to the Index Page</h1>")`
        context is an optional dictionary that can be used to pass data to the template.
        """
        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest):
        # 1. Delete handling (by the name of the button)
        if 'delete' in request.POST:
            try:
                Audit.objects.get(id=request.POST.get('delete')).delete()
                return redirect('index')
            except Audit.DoesNotExist:
                pass

        # 2. Edit handling (by the name of the button)
        elif 'edit' in request.POST:
            try:
                item_id = request.POST.get('edit')
                audit = Audit.objects.get(id=item_id)
                form = self.form_class(instance=audit)

                # Store the ID in the session for later use, otherwise it will be lost
                # and pressing the save button will create a new object
                request.session['editing_id'] = item_id
                return render(request, self.template_name, self.get_context_data(form=form))
            except Audit.DoesNotExist:
                pass

        # 3. Save handling
        editing_id = request.session.get('editing_id')
        form_data = self.form_class(request.POST, request.FILES)

        # If editing_id is set, it means we are editing an existing audit
        if editing_id:
            audit = Audit.objects.get(id=editing_id)
            form_data = self.form_class(request.POST, request.FILES, instance=audit)
            del request.session['editing_id']

        if form_data.is_valid():
            form_data.save()
            return redirect('index')

        return render(request, self.template_name, self.get_context_data(form=form_data))


# -----------------------------------------------------------------------
class SignUpView(View):
    template_name = 'main_app/signup.html'
    form_class = SignUpForm
    page_title = 'Sign Up'
    page_name = 'Create Account'

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),
        }
        return context

    def get(self, request: HttpRequest):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            return redirect('index')

        # If form is invalid, return the form with errors
        return render(request, self.template_name, self.get_context_data(form=form))


class LoginView(View):
    template_name = 'main_app/login.html'
    form_class = LoginForm
    page_title = 'Login'
    page_name = 'Welcome Back'

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),
        }
        return context

    def get(self, request: HttpRequest):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request: HttpRequest):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('index')

        messages.error(request, 'Invalid username or password')
        return render(request, self.template_name, self.get_context_data(form=form))


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')


# -----------------------------------------------------------------------
def about_us_view(request: HttpRequest, some_variable: int):
    use_the_var = some_variable
    return render(request, 'main_app/index.html')


def redirect_from_here_view(request: HttpRequest):
    """
    Redirects to the index view.
    :param request: HttpRequest object.
    :return: HttpResponseRedirect to the index view by its name!
    """
    return redirect('index')
