from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class FuelPriceOption(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = 'Fuel price option'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class GrowingRate(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = 'Growing rate'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Project(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    year_init_optimization = models.IntegerField(default=0, blank=True, null=True)
    year_end_optimization = models.IntegerField(default=0, blank=True, null=True)
    periodicity_auction = models.IntegerField(default=0, blank=True, null=True)
    regasification_init = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)
    file  = models.FileField(upload_to='static/static/configuration_sddp', blank=False, null=False)
    fuel_price_option = models.ForeignKey(FuelPriceOption, on_delete=models.CASCADE, blank=True, null=True)
    growing_rate = models.ForeignKey(GrowingRate, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Project'
        ordering = ['-id']

    def __str__(self):
        return str(self.name)


class GraphYear(models.Model):
    year = models.IntegerField(blank=False, null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Graph year'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class AdditionalCapacity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    year = models.IntegerField(default=0, blank=True, null=True)
    wind = models.FloatField(default=0, blank=True, null=True)
    solar = models.FloatField(default=0, blank=True, null=True)
    pch = models.FloatField(default=0, blank=True, null=True)
    thermal_not_centralized = models.FloatField(default=0, blank=True, null=True)
    liquid = models.FloatField(default=0, blank=True, null=True)
    coal = models.FloatField(default=0, blank=True, null=True)
    gas = models.FloatField(default=0, blank=True, null=True)
    glp = models.FloatField(default=0, blank=True, null=True)
    hidro = models.FloatField(default=0, blank=True, null=True)
    relaxation = models.IntegerField(blank=True, null=True)
    iteration = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Additional capacity'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class MetaMatrix(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    year = models.IntegerField(default=0, blank=True, null=True)
    wind = models.FloatField(default=0, blank=True, null=True)
    solar = models.FloatField(default=0, blank=True, null=True)
    pch = models.FloatField(default=0, blank=True, null=True)
    thermal_not_centralized = models.FloatField(default=0, blank=True, null=True)
    liquid = models.FloatField(default=0, blank=True, null=True)
    coal = models.FloatField(default=0, blank=True, null=True)
    gas = models.FloatField(default=0, blank=True, null=True)
    glp = models.FloatField(default=0, blank=True, null=True)
    hidro = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Meta matrix'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class MaxNewCapacity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    year = models.IntegerField(default=0, blank=True, null=True)
    wind = models.FloatField(default=0, blank=True, null=True)
    solar = models.FloatField(default=0, blank=True, null=True)
    pch = models.FloatField(default=0, blank=True, null=True)
    thermal_not_centralized = models.FloatField(default=0, blank=True, null=True)
    liquid = models.FloatField(default=0, blank=True, null=True)
    coal = models.FloatField(default=0, blank=True, null=True)
    gas = models.FloatField(default=0, blank=True, null=True)
    glp = models.FloatField(default=0, blank=True, null=True)
    hidro = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Max new capacity'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class LcoeEnergyCost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    year = models.IntegerField(default=0, blank=True, null=True)
    wind = models.FloatField(default=0, blank=True, null=True)
    solar = models.FloatField(default=0, blank=True, null=True)
    pch = models.FloatField(default=0, blank=True, null=True)
    thermal_not_centralized = models.FloatField(default=0, blank=True, null=True)
    liquid = models.FloatField(default=0, blank=True, null=True)
    coal = models.FloatField(default=0, blank=True, null=True)
    gas = models.FloatField(default=0, blank=True, null=True)
    glp = models.FloatField(default=0, blank=True, null=True)
    hidro = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Lcoe energy cost'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class Demand(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    demand_at = models.DateField(blank=False, null=False)
    month_days = models.IntegerField(blank=False, null=False)
    value = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Demand'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class PlantType(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    enficc_factor = models.FloatField(default=0, blank=True, null=True)
    flexible = models.BooleanField(default=None, blank=True, null=True)

    class Meta:
        verbose_name = 'Plant type'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Fuel(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)

    class Meta:
        verbose_name = 'Fuel'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class ExistingPlants(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE, blank=True, null=True)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    reliability_obligation = models.FloatField(default=0, blank=True, null=True)
    long_term_contract = models.FloatField(default=0, blank=True, null=True)
    central_dispatch = models.BooleanField(default=None, blank=True, null=True)
    nominal_power = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Existing plants'
        ordering = ['project']

    def __str__(self):
        return str(self.project)


class FuturePlants(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False)
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE, blank=True, null=True)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    reliability_obligation = models.FloatField(default=0, blank=True, null=True)
    long_term_contract = models.FloatField(default=0, blank=True, null=True)
    central_dispatch = models.BooleanField(default=None, blank=True, null=True)
    nominal_power = models.FloatField(default=0, blank=True, null=True)
    start_at = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Future plants'
        ordering = ['project']

    def __str__(self):
        return str(self.project)
