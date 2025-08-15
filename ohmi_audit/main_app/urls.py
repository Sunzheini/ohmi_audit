from django.urls import path
from django.http import HttpResponse
from ohmi_audit.main_app.views import *


urlpatterns = [
    # http://localhost:8000/
    # path('', index_view, name='index'),
    path('', IndexView.as_view(), name='index'),

    #Auth
    # ----------------------------------------------------------------
    # http://localhost:8000/signup/
    path('signup/', SignUpView.as_view(), name='signup'),

    # http://localhost:8000/login/
    path('login/', LoginView.as_view(), name='login'),

    # http://localhost:8000/logout/
    path('logout/', LogoutView.as_view(), name='logout'),

    # API Endpoints
    # ----------------------------------------------------------------
    # http://localhost:8000/api-endpoint-example-model/
    path('api-endpoint-example-model/', ModelEndPointView.as_view(), name='api-endpoint-example-model'),
    path('api-endpoint-example-model/<int:pk>/', ModelEndPointView.as_view(), name='api-endpoint-example-model-pk'),

    # http://localhost:8000/api-endpoint-example-custom-data/
    path('api-endpoint-example-custom-data/', CustomDataEndPointView.as_view(), name='api-endpoint-example-custom-data'),

    # Other Views
    # ----------------------------------------------------------------
    # http://localhost:8000/about-us/3/
    path('about-us/<int:some_variable>/', about_us_view, name='about-us'),

    # http://localhost:8000/redirect-from-here/
    path('redirect-from-here/', redirect_from_here_view, name='redirect-from-here'),

    # Celery Example
    # ----------------------------------------------------------------
    # http://localhost:8000/celery-example/
    path('celery-example/', TaskTestView.as_view(), name='celery-example-view'),
    # status endpoint for Celery tasks
    path('celery-example-task-status/<str:task_id>/', task_status, name='celery-example-task-status'),

    # ----------------------------------------------------------------
    path('health/', lambda request: HttpResponse(status=200)),  # Add this line
]
