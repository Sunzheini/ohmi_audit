from django.http import HttpRequest
from django.shortcuts import render, redirect


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
    context = {
        'page_title': 'Ohmi Audit Test',
        'page_name': 'Welcome',
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
