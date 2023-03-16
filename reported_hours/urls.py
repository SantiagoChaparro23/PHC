from django.urls import path
from django.urls.resolvers import URLPattern
from django.views.generic.base import View
from .views import (
    reported_hours,
    notifications
)


app_name = 'reported_hours'


urlpatterns = [
    path('', reported_hours.ReportedHoursListView.as_view(), name = 'reported_hours_list'),
    path('create', reported_hours.ReportedHoursCreateView.as_view(), name='reported_hours_create'),
    path('confirmation', reported_hours.ReportedHoursConfirmationView.as_view(), name='reported_hours_confirmation'),
    path('<int:pk>/delete', reported_hours.ReportedHoursDeleteView.as_view(), name='reported_hours_delete'),

 
    path('reports', reported_hours.ReportsView.as_view(), name='reported_hours_reports'),
    path('sabana-report',  reported_hours.SabanaView.as_view(), name='sabana'),
    path('excel',  reported_hours.excel, name = 'excel'),

    path('user/<int:pk>',  reported_hours.UserReportView.as_view(), name='user_report'),
    


    path('notifications/daily', notifications.daily, name = 'notifications_daily'),


   
    path('remove/draft/<int:pk>', reported_hours.remove_draft, name = 'remove_draft'),
    path('apply_drafts/', reported_hours.apply_drafts, name = 'apply_drafts'),
   
    # path('/create'),
]
