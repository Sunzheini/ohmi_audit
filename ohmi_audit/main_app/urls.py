from django.urls import path
from ohmi_audit.main_app.views import *


urlpatterns = [
    # http://localhost:8000/
    # path('', index_view, name='index'),
    path('', IndexView.as_view(), name='index'),

    # ----------------------------------------------------------------
    # http://localhost:8000/signup/
    path('signup/', SignUpView.as_view(), name='signup'),

    # http://localhost:8000/login/
    path('login/', LoginView.as_view(), name='login'),

    # http://localhost:8000/logout/
    path('logout/', LogoutView.as_view(), name='logout'),

    # ----------------------------------------------------------------

    # http://localhost:8000/about-us/3/
    path('about-us/<int:some_variable>/', about_us_view, name='about-us'),

    # http://localhost:8000/redirect-from-here/
    path('redirect-from-here/', redirect_from_here_view, name='redirect-from-here'),
]
