from django.db import models
from django.db.models.fields import FloatField
from django.contrib.auth.models import User
# Create your models here.



class Project(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField( blank=True, null=True)
    demand_factor  = models.FloatField(null=True)
    trm  = models.FloatField(null=True)
    trm_date = models.DateField(blank=False, null=False)

    start_date = models.DateField(blank=False, null=False)
    limit_date = models.DateField(blank=False, null=False)

    created_by = models.ForeignKey(User, related_name='Project_created_by', on_delete=models.CASCADE, null=True)
   
    file  = models.FileField(upload_to="storage/sddp/projects", null=True, blank=True)
       
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return str(self.name)

class Demand(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False, default=0)
    block = models.IntegerField( null=False, blank=False)
    date = models.DateField(blank=False, null=False)
    value = models.FloatField(blank=False, null=False)
    



class Db(models.Model):
    name = models.CharField(max_length=255,  blank=False, null=False)
    project = models.ForeignKey(Project, related_name='dbs', on_delete=models.CASCADE, null=False, default=0)
    description = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    plant = models.CharField(max_length=255,  blank=True, null=True)


    cmgdem_file  =     models.FileField(upload_to="storage/sddp/dbs", null=True, blank=True)
    genpltproy_file  = models.FileField(upload_to="storage/sddp/dbs", null=True, blank=True, help_text=' En caso de que sea la base de datos del proyecto, los archivos de generacion o preferiblemente el genpltproy.csv generado por el script que toma los datos de la planta del proyecto, esto agiliza este procedimiento de forma drastica.')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class MarginalCostDemand(models.Model):
    db = models.ForeignKey(Db, on_delete=models.CASCADE, null=False, default=0)
    block = models.IntegerField( null=False, blank=False)
    serie = models.IntegerField( null=True, blank=True)
    date = models.DateField(blank=False, null=False)
    value = models.FloatField(blank=False, null=False)


class Generation(models.Model):
    db = models.ForeignKey(Db, on_delete=models.CASCADE, null=False, default=0)
    block = models.IntegerField( null=False, blank=False)
    serie = models.IntegerField( null=True, blank=True)
    date = models.DateField(blank=False, null=False)
    value = models.FloatField(blank=False, null=False)


class ReturnRate(models.Model):
    year = models.IntegerField( null=False, blank=False)
    value = models.FloatField(blank=False, null=False)
    resolution = models.CharField(max_length=255, blank=False, null=False)
    tension_level = models.CharField(max_length=255, blank=False, null=False)


class WeightBlocks(models.Model):
    block = models.IntegerField( null=False, blank=False)
    weight = models.FloatField( null=False, blank=False)