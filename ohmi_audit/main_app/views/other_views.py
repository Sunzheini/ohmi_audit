"""
Other utility views.
Contains placeholder and utility views like about_us and redirect examples.
"""
from django.http import HttpRequest
from django.shortcuts import render, redirect


def about_us_view(request: HttpRequest, some_variable: int):
    """
    About us page view.
    ToDo: Implement as needed
    """
    use_the_var = some_variable
    return render(request, 'main_app/index.html')


def redirect_from_here_view(request: HttpRequest):
    """
    Redirects to the index view.
    :param request: HttpRequest object.
    :return: HttpResponseRedirect to the index view by its name!
    """
    return redirect('index')

