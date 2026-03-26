"""
Main application views.
Contains the primary IndexView for the main application page.
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


# You can use the get_user_model() function to get the user model
UserModel = get_user_model()
# if UserModel.objects.exists():
#     all_users = list(UserModel.objects.all())
# else:
#     all_users = []
all_users = []


# use the LoginRequiredMixin to ensure that the user is logged in before accessing the view
class IndexView(LoginRequiredMixin, BaseView):
    """
    Main index view for the Ohmi Audit application.
    Handles displaying, creating, editing, and deleting audit records.
    # Change all backslashes (\) to forward slashes (/) if deploying on Render (linux-based servers)
    """
    # -----------------------------------------------------------------------
    # for the LoginRequiredMixin
    # Use the URL name so i18n patterns are respected (prefixes like /en/)
    login_url = 'login'  # URL name, not hard-coded path like '/login/', Redirect to this URL if not logged in
    redirect_field_name = 'next'  # URL parameter to redirect after login

    # -----------------------------------------------------------------------
    def define_basic_elements(self):
        self.template_name = 'main_app/index.html'
        self.form_class = CustomerForm          # Select the correct form for the view
        self.page_title = _('Ohmi Audit Test')  # Mark for translation
        self.page_name = _("Customer's List")

    # -----------------------------------------------------------------------
    # Audit  # Set the model for pagination and for listing
    # add this decorator only if you want to paginate the results
    @paginate_results(model=Customer, items_per_page=10)
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
            'redirect_to': self.request.GET.get('next', ''),  # Add this to ensure language switcher works
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
        # 0. Handle AJAX search request
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                search_query = data.get('search_query', '')
                
                if search_query:
                    # Search across multiple fields in Customer model
                    from django.db.models import Q
                    
                    results = Customer.objects.filter(
                        Q(company_name_bg__icontains=search_query) |
                        Q(company_name_en__icontains=search_query) |
                        Q(BG_Vor_Nr__icontains=search_query) |
                        Q(company_id__icontains=search_query) |
                        Q(year__icontains=search_query)
                    )
                    
                    # Serialize the results
                    results_data = list(results.values())  # Convert to list of dictionaries
                    
                    return JsonResponse({
                        'success': True,
                        'results': results_data,
                        'count': len(results_data)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'No search query provided'
                    }, status=400)
                    
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON'
                }, status=400)
        
        # -----------------------------------------------------------------------
        # 0.5. Invalidate cache when changes are made
        cache_key = f"audit_list_{request.user.id}"
        cache.delete(cache_key)

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
