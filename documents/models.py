from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Area(models.Model):
    area = models.CharField(max_length=50, blank=False, null=False)
    
    class Meta:
        verbose_name = 'Area'
        ordering=['area']
        
        
    def __str__(self):
        return str(self.area) 


class Templates(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=False, null=False)
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=200,blank=False, null=False)
    file = models.FileField(upload_to = 'static/static/documents', blank=False, null=False)  
    created_at = models.DateField(blank=False, null=False) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Templates'
        ordering=['title']

    def __str__(self):
        return str(self.title) 
