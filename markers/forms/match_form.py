from django import forms
from markers.models import Match

class MatchForm(forms.ModelForm):
    
    class Meta:
        model = Match
        
        fields = (
            'local_team',
            'visiting_team',
            'local_goals',
            'away_goals',
        )
        
        labels = {
            'local_team': 'Equipo local',
            'visiting_team': 'Equipo Visitante',
            'local_goals': 'Goles de Local',
            'away_goals': 'Goles de Visitante',
        }