"""datcore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('', include('users.urls', namespace='users')),
    path('imports/', include('imports.urls', namespace='imports')),
    path('api/', include('api.urls', namespace='api')),
    path('lessons/', include('lessons.urls', namespace='lessons')),
    path('sddp/', include('sddp.urls', namespace='sddp')),
    path('budgeted_hours/', include('budgeted_hours.urls', namespace='budgeted_hours')),
    path('reported_hours/', include('reported_hours.urls', namespace='reported_hours')),
    path('record_business_interactions/', include('record_business_interactions.urls', namespace='record_business_interactions')),
    path('vacations/', include('vacations.urls', namespace = 'vacations')),
    path('configuration_sddp/', include('configuration_sddp.urls', namespace = 'configuration_sddp')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('markers/', include('markers.urls', namespace='markers')),
]
 