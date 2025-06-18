from django.urls import path
from ohmi_audit.hr_management.views import *


urlpatterns = [
    # http://localhost:8000/hr-management/
    path('', hr_management_index_view, name='hr-management-index'),
]
