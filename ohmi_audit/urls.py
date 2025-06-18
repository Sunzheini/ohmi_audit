from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ohmi_audit.main_app.urls')),
    path('hr-management/', include('ohmi_audit.hr_management.urls')),
]
