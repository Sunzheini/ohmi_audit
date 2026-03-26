"""
Database Management views.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from common.base_view import BaseView
from common.db_management import DbManagement
from ohmi_audit.main_app.forms import *

logger = logging.getLogger('ohmi_audit')

UserModel = get_user_model()
all_users = []


class DbIndexView(LoginRequiredMixin, BaseView):
    """
    Database management index view for the Ohmi Audit application.
    """
    # -----------------------------------------------------------------------
    login_url = 'login'
    redirect_field_name = 'next'

    # -----------------------------------------------------------------------
    def define_basic_elements(self):
        self.template_name = 'main_app/db_management.html'

        self.delete_db_form = DeleteDatabaseForm()
        self.import_db_form = ImportDatabaseForm()
        self.export_db_form = ExportDatabaseForm()

        self.page_title = _('Ohmi Audit Test')  # Mark for translation
        self.page_name = _("Database Management")

    # -----------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        """Shared context for both GET and POST"""
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),

            'delete_db_form': self.delete_db_form,
            'import_db_form': self.import_db_form,
            'export_db_form': self.export_db_form,

            'message': kwargs.get('message', None),  # Get message from kwargs
        }
        return context

    # -----------------------------------------------------------------------
    def post(self, request: HttpRequest):
        message = None

        # -----------------------------------------------------------------------
        # 1. Delete Database
        if 'delete_db' in request.POST:
            try:
                self.delete_db_form = DeleteDatabaseForm(request.POST)

                if self.delete_db_form.is_valid():
                    message = DbManagement.delete_database()
                    self.delete_db_form = DeleteDatabaseForm()

                self.import_db_form = ImportDatabaseForm()
                self.export_db_form = ExportDatabaseForm()

            except Exception as e:
                logger.error("delete_database form error: %s", e, exc_info=True)
                self.delete_db_form.add_error(None, _("An error occurred during processing."))
                self.import_db_form = ImportDatabaseForm()
                self.export_db_form = ExportDatabaseForm()

        # -----------------------------------------------------------------------
        # 1. Import Database
        elif 'import_db' in request.POST:
            try:
                self.import_db_form = ImportDatabaseForm(request.POST, request.FILES)

                if self.import_db_form.is_valid():
                    uploaded_file = self.import_db_form.cleaned_data['select_file']
                    message = DbManagement.import_from_excel(uploaded_file)
                    self.import_db_form = ImportDatabaseForm()

                self.delete_db_form = DeleteDatabaseForm()
                self.export_db_form = ExportDatabaseForm()

            except Exception as e:
                logger.error("import_from_excel form error: %s", e, exc_info=True)
                self.import_db_form.add_error(None, _("An error occurred during processing."))
                self.delete_db_form = DeleteDatabaseForm()
                self.export_db_form = ExportDatabaseForm()

        # -----------------------------------------------------------------------
        # 1. Export Database
        elif 'export_db' in request.POST:
            try:
                self.export_db_form = ExportDatabaseForm(request.POST)

                if self.export_db_form.is_valid():
                    # export_to_excel() returns an HttpResponse with the file
                    # attached – return it immediately to trigger the download.
                    return DbManagement.export_to_excel()

                self.delete_db_form = DeleteDatabaseForm()
                self.import_db_form = ImportDatabaseForm()

            except Exception as e:
                logger.error("export_to_excel form error: %s", e, exc_info=True)
                self.export_db_form.add_error(None, _("An error occurred during processing."))
                self.delete_db_form = DeleteDatabaseForm()
                self.import_db_form = ImportDatabaseForm()

        return render(request, self.template_name, self.get_context_data(message=message))
