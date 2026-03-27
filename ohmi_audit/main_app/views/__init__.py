"""
Views package for the main_app.
Exposes all views for backward compatibility with existing imports.
"""
# Main views
from .main_views import IndexView

# Authentication views
from .auth_views import SignUpView, LoginView, LogoutView

# API endpoint views
from .api_views import ModelEndPointView, CustomDataEndPointView

# Celery task views
from .task_views import TaskTestView, task_status

# Other utility views
from .other_views import about_us_view, redirect_from_here_view


# Export all views for import with 'from ohmi_audit.main_app.views import *'
__all__ = [
    # Main views
    'IndexView',
    
    # Auth views
    'SignUpView',
    'LoginView',
    'LogoutView',
    
    # API views
    'ModelEndPointView',
    'CustomDataEndPointView',
    
    # Task views
    # 'TaskTestView',
    # 'task_status',
    
    # Other views
    'about_us_view',
    'redirect_from_here_view',
]

