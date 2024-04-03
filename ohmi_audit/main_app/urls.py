from django.urls import path
from ohmi_audit.main_app.views import index_view


urlpatterns = [
    path('', index_view, name='index'),
]
