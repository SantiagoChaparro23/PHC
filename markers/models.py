from django.db import models

# Create your models here.


class Team(models.Model):
    
    name = models.CharField(max_length=50, blank=False, null=False)
    
    class Meta:
        verbose_name = 'Team'
        ordering = ['name']
        
        
    def __str__(self):
        return str(self.name)

    
class Match(models.Model):
    
    local_team = models.ForeignKey(Team,on_delete=models.CASCADE, blank=False, null=False, related_name='local_team')
    visiting_team = models.ForeignKey(Team,on_delete=models.CASCADE, blank=False, null=False, related_name='visiting_team')
    local_goals = models.IntegerField(default=0)
    away_goals = models.IntegerField(default=0)
    
    def __str__ (self):
        return f'{self.local_team} vs {self.visiting_team}'
    
