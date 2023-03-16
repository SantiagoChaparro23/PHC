from django.urls import path
from .views import (
    phenomenon,
    metric,
    files_metric,
    downloads,
    index,
    search
)


app_name = 'dashboard'


urlpatterns = [



    path('', index.index, name='home'),


    path('meec/standar', index.standar, name='standar'),
    path('meec/standar/generation', index.generation_api, name='generation'),
    path('search', search.index, name='search'),
    path('search/get-component', search.get_components_by_metric, name='get_components_by_metric'),
  



    path('lang', phenomenon.set_language, name='set_language'),

    path('phenomenons', phenomenon.PhenomenonListView.as_view(), name='phenomenon_list'),
    path('phenomenons/create', phenomenon.PhenomenonCreateView.as_view(), name='phenomenon_create'),
    path('phenomenons/<int:pk>', phenomenon.PhenomenonDetailView.as_view(), name='phenomenon_view'),
    path('phenomenons/<int:pk>/delete', phenomenon.PhenomenonDeleteView.as_view(), name='phenomenon_delete'),

    path('metrics', metric.MetricListView.as_view(), name = 'metrics_list'),
    path('metrics/create', metric.MetricCreateView.as_view(), name = 'metric_create'),
    path('metrics/<int:pk>', metric.MetricDetailView.as_view(), name = 'metric_view'),
    path('metrics/<int:pk>/delete', metric.MetricDeleteView.as_view(), name = 'metric_delete'),

    path('files_metrics', files_metric.UrlsFilesMetricListView.as_view(), name = 'files_metrics_list'),
    path('files_metrics/create', files_metric.UrlsFilesMetricCreateView.as_view(), name = 'files_metrics_create'),
    path('files_metrics/<int:pk>', files_metric.UrlsFilesMetricDetailView.as_view(), name = 'files_metrics_view'),
    path('files_metrics/<int:pk>/delete', files_metric.UrlsFilesMetricDeleteView.as_view(), name = 'files_metrics_delete'),
    path('files_metrics/<int:pk>/process', files_metric.UrlsFilesMetricProcessView.as_view(), name = 'files_metrics_process'),

    path('standard_downloads', downloads.standard_downloads, name = 'standard_downloads')

]
