from django.urls import path
from .views import (
    index,
    download_graphed_data
)


app_name = 'api'


urlpatterns = [
    path('', index, name='api'),
    path('download_graphed_data', download_graphed_data, name='download_graphed_data'),
   
]
