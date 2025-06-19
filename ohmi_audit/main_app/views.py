from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ohmi_audit.main_app.forms import *
from ohmi_audit.main_app.models import Audit


def index_view(request: HttpRequest):
    """
    # Index View
    :param request: Even though `request` is technically WSGIRequest, you can type-hint it as
    HttpRequest for clarity.
    :return: HttpResponse rendering the index page through the render function. You can also
    return a simple HttpResponse with raw HTML content:
    `return HttpResponse("<h1>Welcome to the Index Page</h1>")`
    context is an optional dictionary that can be used to pass data to the template.
    """
    if request.method == 'POST':
        # Check if this is a delete request
        if 'delete_id' in request.POST:
            try:
                audit = Audit.objects.get(id=request.POST['delete_id'])
                audit.delete()
                return redirect('index')
            except Audit.DoesNotExist:
                pass
        # Otherwise handle form submission
        else:
            form = AuditForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
    else:
        form = AuditForm()

    context = {
        'page_title': 'Ohmi Audit Test',
        'page_name': 'Welcome',
        'audit_list': Audit.objects.all(),
        'form': form,  # Pass the form instance, not the class
    }

    return render(request, 'index.html', context)


def about_us_view(request: HttpRequest, some_variable: int):
    use_the_var = some_variable
    return render(request, 'index.html')


def redirect_from_here_view(request: HttpRequest):
    """
    Redirects to the index view.
    :param request: HttpRequest object.
    :return: HttpResponseRedirect to the index view by its name!
    """
    return redirect('index')
