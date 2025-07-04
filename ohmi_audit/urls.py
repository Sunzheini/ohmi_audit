from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('ohmi_audit.main_app.urls')),
    path('hr-management/', include('ohmi_audit.hr_management.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Internationalization patterns
urlpatterns += i18n_patterns(
    path('', include('ohmi_audit.main_app.urls')),
    path('hr-management/', include('ohmi_audit.hr_management.urls')),
    prefix_default_language=False
)
"""
prefix_default_language=False  
# Do not prefix URLs with the default language code
# This allows URLs to be accessed without the language code if the default language is used
# If you want to prefix URLs with the default language code, set this to True
"""
