from django.urls import path
from .views import (
    documents,
    area
)


app_name = 'documents'


urlpatterns = [
    path('documents', documents.DocumentsListView.as_view(), name = 'documents_list'),   
    path('documents/create', documents.DocumentsCreateView.as_view(), name = 'documents_create'),
    path('documents/<int:pk>/detail', documents.DocumentsDetailView.as_view(), name = 'documents_detail'),
    path('documents/<int:pk>/change', documents.DocumentsUpdateView.as_view(), name = 'documents_change'),
    path('documents/<int:pk>/delete', documents.DocumentsDeleteView.as_view(), name = 'documents_delete'),
    
    path('area', area.AreaListView.as_view(), name = 'area_list'),   
    path('area/create', area.AreaCreateView.as_view(), name = 'area_create'),
    path('area/<int:pk>/change', area.AreaUpdateView.as_view(), name = 'area_change'),
    path('area/<int:pk>/delete', area.AreaDeleteView.as_view(), name = 'area_delete'),
]


