from django import db
from django.urls import path
from .views import (
    projects, dbs, returnrate, weightblocks, operationalbenefits
)


app_name = 'sddp'


urlpatterns = [

    path('operational-benefits', operationalbenefits.TemplateView.as_view(), name='operational_benefits'),
    path('operational-benefits/dbs', operationalbenefits.get_dbs, name='get_dbs'),
    path('operational-benefits/get-operationalbenefits', operationalbenefits.get_operationalbenefits, name='get_operationalbenefits'),
    path('operational-benefits/download-operationalbenefits', operationalbenefits.download_operationalbenefits, name='download_operationalbenefits'),

    path('projects', projects.ProjectsListView.as_view(), name='projects_list'),
    path('projects/create', projects.ProjectCreateView.as_view(), name='projects_create'),
    path('projects/<int:pk>/delete', projects.ProjectDeleteView.as_view(), name='projects_delete'),

    path('dbs', dbs.DbsListView.as_view(), name='dbs_list'),
    path('dbs/create', dbs.DbsCreateView.as_view(), name='dbs_create'),
    path('dbs/<int:pk>/delete', dbs.DbsDeleteView.as_view(), name='dbs_delete'),

    path('return-rate', returnrate.ReturnRateListView.as_view(), name='returnrate_list'),
    path('return-rate/create', returnrate.ReturnRateCreateView.as_view(), name='returnrate_create'),
    path('return-rate/<int:pk>/delete', returnrate.ReturnRateDeleteView.as_view(), name='returnrate_delete'),
    path('return-rate/<int:pk>/change', returnrate.ReturnRateChangeView.as_view(), name='returnrate_change'),
  
    path('weight-blocks', weightblocks.WeightBlocksListView.as_view(), name='weightblocks_list'),
    path('weight-blocks/create', weightblocks.WeightBlocksCreateView.as_view(), name='weightblocks_create'),
    path('weight-blocks/<int:pk>/delete', weightblocks.WeightBlocksDeleteView.as_view(), name='weightblocks_delete'),
    path('weight-blocks/<int:pk>/change', weightblocks.WeightBlocksChangeView.as_view(), name='weightblocks_change'),
 
]

