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
    # GET and POST are the only HTTP methods to use when dealing with forms in Django.
    if request.method == 'POST':

        # Check if this is a delete request by the name of the button
        if 'delete' in request.POST:
            try:
                audit = Audit.objects.get(id=request.POST.get('delete'))
                audit.delete()
                return redirect('index')
            except Audit.DoesNotExist:
                pass

        # Check if this is an edit request by the name of the button
        elif 'edit' in request.POST:
            try:
                item_id = request.POST.get('edit')
                audit = Audit.objects.get(id=item_id)
                form = AuditForm(instance=audit)  # Use instance to pre-fill the form

                # Store the ID in the session for later use, otherwise it will be lost
                # and pressing the save button will create a new object
                request.session['editing_id'] = item_id
            except Audit.DoesNotExist:
                form = AuditForm()

        # Save button was pressed then (for both create and edit)
        else:
            editing_id = request.session.get('editing_id')

            # If editing_id is set, it means we are editing an existing audit
            if editing_id:
                audit = Audit.objects.get(id=editing_id)
                form = AuditForm(request.POST, instance=audit)
                del request.session['editing_id']  # Clean up

            # If editing_id is not set, it means we are creating a new audit
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
