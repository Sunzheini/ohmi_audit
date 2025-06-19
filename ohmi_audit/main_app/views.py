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
        form = AuditForm(request.POST)
        if form.is_valid():
            # 1. Save main Audit object first
            audit = form.save(commit=False)
            audit.save()  # This generates the ID

            # 2. Now handle auditors separately
            # Example: Get selected auditor IDs from request.POST
            auditor_ids = request.POST.getlist('auditors')  # Assuming multi-select field
            audit.related_auditors.set(auditor_ids)

            return redirect('index')
    else:
        form = AuditForm()

    context = {
        'page_title': 'Ohmi Audit Test',
        'page_name': 'Welcome',
        'audit_list': Audit.objects.all(),
        'audit_form': form,    # Pass the form instance, not the class
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
