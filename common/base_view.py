from abc import ABC, abstractmethod

from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class BaseView(View, ABC):
    def __init__(self, **kwargs):
        self.template_name, self.form_class, self.page_title, self.page_name = None, None, None, None
        self.define_basic_elements()
        super().__init__(**kwargs)

    @abstractmethod
    def define_basic_elements(self):
        self.template_name, self.form_class, self.page_title, self.page_name = None, None, None, None

    def get_context_data(self, **kwargs):
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),
            'message': None,  # Placeholder for any messages
            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),
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
