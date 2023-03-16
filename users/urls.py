from django.urls import path
from .views import login_view, logout_view, microsoft_login, microsoft_request_token, microsoft_token


app_name = 'users'


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('login/microsoft', microsoft_login, name='microsoft_login'),
    path('m/microsoft', microsoft_request_token, name='microsoft_callback'),
    
    path('m/microsoftt', microsoft_token, name='microsoftt'),
]
