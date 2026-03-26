"""
Database Management views.
"""
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from common.base_view import BaseView
from common.pagination_decorator import paginate_results
from ohmi_audit.main_app.forms import *
from ohmi_audit.main_app.models import *

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

        self.form_class_delete_db = DeleteDatabaseForm
        self.form_class_import_db = ImportDatabaseForm
        self.form_class_export_db = ExportDatabaseForm

        self.page_title = _('Ohmi Audit Test')  # Mark for translation
        self.page_name = _("Database Management")

    # -----------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        """Shared context for both GET and POST"""
        cache_key = f"audit_list_{self.request.user.id}"  # User-specific cache
        cached_data = cache.get(cache_key)

        if not cached_data:
            all_items = Customer.objects.all()
            cache.set(cache_key, all_items, timeout=60)  # Cache for 5 minutes
        else:
            all_items = cached_data

        # -----------------------------------------------------------------------
        context = {
            'page_title': self.page_title,
            'page_name': self.page_name,
            'redirect_to': self.request.GET.get('next', ''),
            'data_for_content_container_wrapper_top': kwargs.get('form', self.form_class()),
            # Pass the form instance, not the class

            'message': None,  # Placeholder for any messages
            'data_for_content_container_wrapper_bottom': all_items,

            'card_button_1_name': _('New Record'),  # Mark for translation
            'card_button_2_name': _('Search'),
            'form_visibility': kwargs.get('form_visibility', "none"),
        }
        return context

    # -----------------------------------------------------------------------
    def post(self, request: HttpRequest):
        # -----------------------------------------------------------------------
        # 1. Delete handling (by the name of the button)
        if 'delete' in request.POST:
            try:
                Customer.objects.get(id=request.POST.get('delete')).delete()
                return redirect('index')
            except Customer.DoesNotExist:
                pass

        # -----------------------------------------------------------------------
        # 2. Edit handling (by the name of the button)
        elif 'edit' in request.POST:
            try:
                item_id = request.POST.get('edit')
                audit = Customer.objects.get(id=item_id)
                form = self.form_class(instance=audit)

                # Store the ID in the session for later use, otherwise it will be lost
                # and pressing the save button will create a new object
                request.session['editing_id'] = item_id
                return render(request, self.template_name, self.get_context_data(form=form, form_visibility="block"))
            except Customer.DoesNotExist:
                pass

        # -----------------------------------------------------------------------
        # 3. Continue editing / Handling Save
        editing_id = request.session.get('editing_id')
        form_data = self.form_class(request.POST, request.FILES)

        # a) If editing_id is set, it means we are editing an existing audit
        if editing_id:
            audit = Customer.objects.get(id=editing_id)
            form_data = self.form_class(request.POST, request.FILES, instance=audit)
            del request.session['editing_id']

        # b) If not editing, we are creating a new audit
        if form_data.is_valid():
            form_data.save()
            return redirect('index')

        return render(request, self.template_name, self.get_context_data(form=form_data, form_visibility="block"))
