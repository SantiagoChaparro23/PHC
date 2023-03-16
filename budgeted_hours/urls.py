from django.urls import path
from .views import (
    client,
    activity,
    categories,
    software,
    operator,
    templates_budgeted_hours,
    budgeted_hours,
    budgeted_hours_files,
    traceability_budgeted_hours,
    price_request_format,
)


app_name = 'budgeted_hours'


urlpatterns = [
    path('test', budgeted_hours.test, name = 'test'),
    path('clients', client.ClientListView.as_view(), name = 'clients_list'),
    path('client/create', client.ClientCreateView.as_view(), name = 'client_create'),
    path('client/<int:pk>', client.ClientDetailView.as_view(), name = 'client_view'),
    path('client/<int:pk>/delete', client.ClientDeleteView.as_view(), name = 'client_delete'),
    path('client/client_import', client.client_import, name = 'client_import'),

    path('activity', activity.ActivitiesListView.as_view(), name = 'activity_list'),
    path('activity/create', activity.ActivitiesCreateView.as_view(), name = 'activity_create'),
    path('activity/<int:pk>', activity.ActivitiesUpdateView.as_view(), name = 'activity_view'),
    path('activity/<int:pk>/delete', activity.ActivitiesDeleteView.as_view(), name = 'activity_delete'),

    path('categories', categories.CategoriesListView.as_view(), name = 'categories_list'),
    path('category/create', categories.CategoriesCreateView.as_view(), name = 'category_create'),
    path('category/<int:pk>', categories.CategoriesUpdateView.as_view(), name = 'category_view'),

    path('softwares', software.SoftwaresListView.as_view(), name = 'softwares_list'),
    path('softwares/create', software.SoftwaresCreateView.as_view(), name = 'softwares_create'),
    path('softwares/<int:pk>', software.SoftwaresUpdateView.as_view(), name = 'softwares_view'),
    path('softwares/<int:pk>/delete', software.SoftwaresDeleteView.as_view(), name = 'softwares_delete'),

    path('operators', operator.OperatorListView.as_view(), name = 'operators_list'),
    path('operator/create', operator.OperatorCreateView.as_view(), name = 'operator_create'),
    path('operator/<int:pk>', operator.OperatorUpdateView.as_view(), name = 'operator_view'),
    path('operator/<int:pk>/delete', operator.OperatorDeleteView.as_view(), name = 'operator_delete'),

    path('templates_budgeted_hours', templates_budgeted_hours.TemplatesBudgetedHoursListView.as_view(), name = 'templates_budgeted_hours_list'),
    path('templates_budgeted_hours/create', templates_budgeted_hours.TemplatesBudgetedHoursCreateView.as_view(), name = 'templates_budgeted_hours_create'),
    path('templates_budgeted_hours/<int:pk>', templates_budgeted_hours.TemplatesBudgetedHoursUpdateView.as_view(), name = 'templates_budgeted_hours_view'),
    path('templates_budgeted_hours/activities_by_service_template', templates_budgeted_hours.activities_by_service_template, name = 'activities_by_service_template'),
    path('templates_budgeted_hours/templates_budgeted_hours_update', templates_budgeted_hours.templates_budgeted_hours_update, name = 'templates_budgeted_hours_update'),
    path('templates_budgeted_hours/hours_templates', templates_budgeted_hours.hours_templates, name = 'hours_templates'),

    path('budgeted_hours', budgeted_hours.BudgetedHoursListView.as_view(), name = 'budgeted_hours_list'),
    path('budgeted_hours/create', budgeted_hours.BudgetedHoursCreateView.as_view(), name = 'budgeted_hours_create'),
    path('budgeted_hours/<int:pk>', budgeted_hours.BudgetedHoursDetailView.as_view(), name = 'budgeted_hours_view'),
    path('budgeted_hours/<int:pk>/delete', budgeted_hours.BudgetedHoursDeleteView.as_view(), name = 'budgeted_hours_delete'),
    path('budgeted_hours/activities_by_service', budgeted_hours.activities_by_service, name = 'activities_by_service'),
    path('budgeted_hours/budgeted_hours_update', budgeted_hours.budgeted_hours_update, name = 'budgeted_hours_update'),
    path('budgeted_hours/budgeted_hours_add', budgeted_hours.budgeted_hours_add, name = 'budgeted_hours_add'),
    path('budgeted_hours/send_mail', budgeted_hours.send_mail, name = 'send_mail'),
    path('budgeted_hours/reviewed', budgeted_hours.reviewed, name = 'reviewed'),
    path('budgeted_hours/hours_import', budgeted_hours.hours_import, name = 'hours_import'),
    path('budgeted_hours/history', budgeted_hours.budgeted_hours_history, name = 'budgeted_hours_history'),
    path('budgeted_hours/history/data', budgeted_hours.budgeted_hours_history_data, name = 'budgeted_hours_history_data'),
    path('budgeted_hours/download', budgeted_hours.download_budgeted_hours, name = 'budgeted_hours_download'),

    path('budgeted_hours/files/<int:pk>', budgeted_hours_files.BudgetedHoursFilesUpdateView.as_view(), name='budgeted_hours_files_list'),

    path('traceability_budgeted_hours', traceability_budgeted_hours.TraceabilityBudgetedHoursListView.as_view(), name = 'traceability_budgeted_hours_list'),
    path('traceability_budgeted_hours/<int:pk>/view', traceability_budgeted_hours.TraceabilityBudgetedHoursDetailView.as_view(), name = 'traceability_budgeted_hours_view'),

    path('price_request_format', price_request_format.PriceRequestFormatListView.as_view(), name = 'price_request_format_list'),
    path('price_request_format/create', price_request_format.PriceRequestFormatCreateView.as_view(), name = 'price_request_format_create'),
    path('price_request_format/<int:pk>/update', price_request_format.PriceRequestFormatUpdateView.as_view(), name = 'price_request_format_update'),
]
