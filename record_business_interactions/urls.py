from django.urls import path
from .views import (
    interaction_type,
    visit_record,
    query
)


app_name = 'record_business_interactions'


urlpatterns = [

    path('query', query.query, name='query'),

    path('visit_record', visit_record.VisitRecordListView.as_view(), name='visit_record_list'),
    path('visit_record/create', visit_record.VisitRecordCreateView.as_view(), name='visit_record_create'),
    path('visit_record/<int:pk>/view', visit_record.VisitRecordDetailView.as_view(), name='visit_record_detail'),
    path('visit_record/<int:pk>/change', visit_record.VisitRecordChangeView.as_view(), name='visit_record_change'),
    path('visit_record/<int:pk>/delete', visit_record.VisitRecordDeleteView.as_view(), name='visit_record_delete'),
    path('visit_record/<int:pk>/validate', visit_record.VisitRecordValidateView.as_view(), name='visit_record_validate'),

    path('interaction_type', interaction_type.InteractionTypeListView.as_view(), name='interaction_type_list'),
    path('interaction_type/create', interaction_type.InteractionTypeCreateView.as_view(), name='interaction_type_create'),
    path('interaction_type/<int:pk>/change', interaction_type.InteractionTypeChangeView.as_view(), name='interaction_type_change'),
    path('interaction_type/<int:pk>/delete', interaction_type.InteractionTypeDeleteView.as_view(), name='interaction_type_delete')

]