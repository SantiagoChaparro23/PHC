from django.urls import path
from .views import (
    electrical_studies,
    consultancies,
    protection_coordination_studies,
    connection_studies,
    market_studies,
    reports
)


app_name = 'lessons'


urlpatterns = [
    path('electrical-studies', electrical_studies.ElectricalStudiesListView.as_view(), name='electrical_studies_list'),
    path('electrical-studies/create', electrical_studies.ElectricalStudiesCreateView.as_view(), name='electrical_studies_create'),
    path('electrical-studies/<int:pk>/view', electrical_studies.ElectricalStudiesDetailView.as_view(), name='electrical_studies_detail'),
    path('electrical-studies/<int:pk>/change', electrical_studies.ElectricalStudiesUpdateView.as_view(), name='electrical_studies_change'),
    path('electrical-studies/<int:pk>/delete', electrical_studies.ElectricalStudiesDeleteView.as_view(), name='electrical_studies_delete'),

    path('consultancies', consultancies.ConsultanciesListView.as_view(), name='consultancies_list'),
    path('consultancies/create', consultancies.ConsultanciesCreateView.as_view(), name='consultancies_create'),
    path('consultancies/<int:pk>/view', consultancies.ConsultanciesDetailView.as_view(), name='consultancies_detail'),
    path('consultancies/<int:pk>/change', consultancies.ConsultanciesUpdateView.as_view(), name='consultancies_change'),
    path('consultancies/<int:pk>/delete', consultancies.ConsultanciesDeleteView.as_view(), name='consultancies_delete'),

    path('protection-coordination-studies', protection_coordination_studies.ProtectionCoordinationStudiesListView.as_view(), name='protection_coordination_studies_list'),
    path('protection-coordination-studies/create', protection_coordination_studies.ProtectionCoordinationStudiesCreateView.as_view(), name='protection_coordination_studies_create'),
    path('protection-coordination-studies/<int:pk>/view', protection_coordination_studies.ProtectionCoordinationStudiesDetailView.as_view(), name='protection_coordination_studies_detail'),
    path('protection-coordination-studies/<int:pk>/change', protection_coordination_studies.ProtectionCoordinationStudiesUpdateView.as_view(), name='protection_coordination_studies_change'),
    path('protection-coordination-studies/<int:pk>/delete', protection_coordination_studies.ProtectionCoordinationStudiesDeleteView.as_view(), name='protection_coordination_studies_delete'),

    path('connection-studies', connection_studies.ConnectionStudiesListView.as_view(), name='connection_studies_list'),
    path('connection-studies/create', connection_studies.ConnectionStudiesCreateView.as_view(), name='connection_studies_create'),
    path('connection-studies/<int:pk>/view', connection_studies.ConnectionStudiesDetailView.as_view(), name='connection_studies_detail'),
    path('connection-studies/<int:pk>/change', connection_studies.ConnectionStudiesChangeView.as_view(), name='connection_studies_change'),
    path('connection-studies/<int:pk>/delete', connection_studies.ConnectionStudiesDeleteView.as_view(), name='connection_studies_delete'),

    path('connection-studies/operatos', connection_studies.getOperators, name='operatos'),
    path('connection-studies/areas', connection_studies.getAreas, name='areas'),

    path('market-studies', market_studies.MarketStudiesListView.as_view(), name='market_studies_list'),
    path('market-studies/create', market_studies.MarketStudiesCreateView.as_view(), name='market_studies_create'),
    path('market-studies/<int:pk>/view', market_studies.MarketStudiesDetailView.as_view(), name='market_studies_detail'),
    path('market-studies/<int:pk>/change', market_studies.MarketStudiesChangeView.as_view(), name='market_studies_change'),
    path('market-studies/<int:pk>/delete', market_studies.MarketStudiesDeleteView.as_view(), name='market_studies_delete'),

    path('reports', reports.ReportsTemplateView.as_view(), name='reports_lessons'),

    # path('commercial', commercial.CommercialListView.as_view(), name='commercial_list'),
    # path('commercial/create', commercial.CommercialCreateView.as_view(), name='commercial_create'),
    # path('commercial/<int:pk>/view', commercial.CommercialDetailView.as_view(), name='commercial_detail'),
    # path('commercial/<int:pk>/change', commercial.CommercialChangeView.as_view(), name='commercial_change'),
    # path('commercial/<int:pk>/delete', commercial.CommercialDeleteView.as_view(), name='commercial_delete'),

    # path('related_area', related_areas.RelatedAreaListView.as_view(), name='related_area_list'),
    # path('related_area/create', related_areas.RelatedAreaCreateView.as_view(), name='related_area_create'),
    # path('related_area/<int:pk>/change', related_areas.RelatedAreaChangeView.as_view(), name='related_area_change'),
    # path('related_area/<int:pk>/delete', related_areas.RelatedAreaDeleteView.as_view(), name='related_area_delete'),

    # path('connection-studies/<int:pk>/view', connection_studies.ConnectionStudiesDetailView.as_view(), name='connection_studies_detail'),

    # path('market-studies/<int:pk>/view', market_studies.MarketStudiesDetailView.as_view(), name='market_studies_detail'),

    # path('market-studies/files/<int:pk>', market_studies_files.MarketStudiesFilesChangeView.as_view(), name='market_studies_list_files'),

    # path('market-studies/information-types', market_studies.get_information_types, name='information_types'),
    # path('market-studies/characteristics', market_studies.get_characteristics, name='characteristics'),

]