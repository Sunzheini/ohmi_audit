from abc import ABC, abstractmethod

from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class BaseView(View, ABC):
    def __init__(self, **kwargs):
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

    def get(self, request: HttpRequest):
        return render(request, self.template_name, self.get_context_data())
