from django.urls import path
from .views import (
    collaborator,
    settings,
    bonus,
    requests,
    requests_files,
    days_caused,
    daily_routine
)


app_name = 'vacations'


urlpatterns = [
    path('collaborators', collaborator.CollaboratorListView.as_view(), name = 'collaborators_list'),
    # path('collaborators/savanna', collaborator.CollaboratorSavannaListView.as_view(), name = 'collaborators_savanna_list'),
    path('collaborator/create', collaborator.CollaboratorCreateView.as_view(), name = 'collaborator_create'),
    path('collaborator/<int:pk>/change', collaborator.CollaboratorUpdateView.as_view(), name = 'collaborator_change'),
    path('collaborator/<int:pk>/delete', collaborator.CollaboratorDeleteView.as_view(), name = 'collaborator_delete'),
    path('collaborators/download', collaborator.download_collaborators, name = 'download_collaborators'),

    path('settings/<int:pk>/change', settings.SettingsUpdateView.as_view(), name = 'settings_change'),
    path('settings/<int:pk>/detail', settings.SettingsDetailView.as_view(), name = 'settings_detail'),

    path('bonus', bonus.BonusListView.as_view(), name = 'bonus_list'),
    path('bonus/create', bonus.BonusCreateView.as_view(), name = 'bonus_create'),
    path('bonus/<int:pk>/change', bonus.BonusUpdateView.as_view(), name = 'bonus_change'),
    path('bonus/<int:pk>/delete', bonus.BonusDeleteView.as_view(), name = 'bonus_delete'),

    path('days_caused', days_caused.DaysCausedListView.as_view(), name = 'days_caused_list'),
    path('days_caused/create', days_caused.DaysCausedCreateView.as_view(), name = 'days_caused_create'),
    path('days_caused/<int:pk>/change', days_caused.DaysCausedUpdateView.as_view(), name = 'days_caused_change'),
    path('days_caused/<int:pk>/delete', days_caused.DaysCausedDeleteView.as_view(), name = 'days_caused_delete'),

    path('requests', requests.RequestsListView.as_view(), name='requests_list'),
    path('requests/savanna', requests.RequestSavannaListView.as_view(), name='request_savanna_list'),
    path('requests/create', requests.RequestsCreateView.as_view(), name='requests_create'),
    path('requests/<int:pk>/detail', requests.RequestsDetailView.as_view(), name='requests_detail'),
    # path('requests/<int:pk>/detail_savanna', requests.RequestsSavannaDetailView.as_view(), name='requests_savanna_detail'),
    path('requests/<int:pk>/change', requests.RequestsChangeView.as_view(), name='requests_change'),
    path('requests/<int:pk>/delete', requests.RequestsDeleteView.as_view(), name='requests_delete'),
    # path('collaborator/download', collaborator.do)

    path('requests/<int:pk>/liquidation', requests.liquidation, name = 'liquidation'),
    path('requests/<int:pk>/change/leader', requests.LeaderStateChangeView.as_view(), name='requests_leader_change'),
    path('requests/<int:pk>/change/final_acceptor', requests.FinalAcceptorStateChangeView.as_view(), name='requests_final_acceptor_change'),
    path('requests/<int:pk>/change/liquidation', requests.LiquidationStateChangeView.as_view(), name='requests_liquidation_change'),
    path('requests/files/<int:pk>', requests_files.RequestsFilesUpdateView.as_view(), name='requests_files_list'),

    path('daily_routine', daily_routine.daily_routine, name='daily_routine'),

    path('_load_historic', requests._load_historic, name='_load_historic'),
    path('_create_colaborators', requests._create_colaborators, name='_create_colaborators'),

]
