from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.utils.translation import gettext_lazy as _

from common.pagination_decorator import paginate_results
from ohmi_audit.main_app.forms import *
from ohmi_audit.main_app.models import Audit

# You can use the get_user_model() function to get the user model
UserModel = get_user_model()
# if UserModel.objects.exists():
#     all_users = list(UserModel.objects.all())
# else:
#     all_users = []
all_users = []
# -----------------------------------------------------------------------


# use the LoginRequiredMixin to ensure that the user is logged in before accessing the view
class IndexView(LoginRequiredMixin, View):
    # Change all backslashes (\) to forward slashes (/) if deploying on Render (linux-based servers)
    template_name = 'main_app/index.html'
    form_class = AuditForm
    page_title = _('Ohmi Audit Test')  # Mark for translation
    page_name = _('Welcome')

    # for the LoginRequiredMixin
    login_url = '/login/'  # Redirect to this URL if not logged in
    redirect_field_name = 'next'  # URL parameter to redirect after login

    # add this decorator only if you want to paginate the results
    @paginate_results(model=Audit, items_per_page=1)
    def get_context_data(self, **kwargs):
        """Shared context for both GET and POST"""
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),  # Add this to ensure language switcher works
            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),
            # Pass the form instance, not the class

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
    template_name = 'main_app/index.html'
    form_class = SignUpForm
    page_title = _('Sign Up')
    page_name = _('Create Account')

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),
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
            messages.success(request,
                             _('Account created successfully! Welcome, %(first_name)s!') % {
                                 'first_name': user.first_name
                             }
                             )
            return redirect('index')

        # If form is invalid, return the form with errors
        return render(request, self.template_name, self.get_context_data(form=form))


class LoginView(View):
    template_name = 'main_app/index.html'
    form_class = LoginForm
    page_title = _('Login')
    page_name = _('Login to Your Account')

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),
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
                messages.success(request,
                                 _('Welcome back, %(first_name)s!') % {
                                     'first_name': user.first_name
                                 }
                                 )
                return redirect('index')

        messages.error(request, _('Invalid username or password'))
        return render(request, self.template_name, self.get_context_data(form=form))


class LogoutView(View):
    @staticmethod
    def get(request):
        logout(request)
        messages.success(request, _('You have been successfully logged out.'))
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
