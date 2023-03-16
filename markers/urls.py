from django.urls import path
from markers.views import (
    team,
    match   
)



app_name = 'markers'

urlpatterns = [
    path('match', match.MatchListView.as_view(), name = 'match_list'),   
    path('match/create', match.MatchCreateView.as_view(), name = 'match_create'),
    path('match/<int:pk>/detail', match.MatchDetailView.as_view(), name = 'match_detail'),
    path('match/<int:pk>/change', match.MatchUpdateView.as_view(), name = 'match_change'),
    path('match/<int:pk>/delete', match.MatchDeleteView.as_view(), name = 'match_delete'),
    
    path('team', team.TeamListView.as_view(), name = 'team_list'),   
    path('team/create', team.TeamCreateView.as_view(), name = 'team_create'),
    path('team/<int:pk>/detail', team.TeamDetailView.as_view(), name = 'team_detail'),
    path('team/<int:pk>/change', team.TeamUpdateView.as_view(), name = 'team_change'),
    path('team/<int:pk>/delete', team.TeamDeleteView.as_view(), name = 'team_delete'),
]