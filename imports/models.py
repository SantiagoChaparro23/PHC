from django.db import models

# --------------------------------------------------------------------
# Indexes of components, metrics, files of metrics and extra info ----
# --------------------------------------------------------------------
RESAMPLES = [
    ('min', 'Mínimo'),
    ('max', 'Máximo'),
    ('sum', 'Sumatoria'),
    ('avg', 'Promedio'),
]

FORMAT = [
    (1, 'Formato 1'),
    (2, 'Formato 2')
]

# BE CAREFUL WHEN MODIFYING THIS
# Modifying the ORDER of these elements can alter 
# the operation of many elements of the entire program, 
# adding periodicities following the order of all the other elements
PERIODICITY = [
    (1, 'Decada'),
    (2, 'Anual'),
    (3, 'Trimestral'),
    (4, 'Mensual'),
    (5, 'Semanal'),
    (6, 'Diaria'),
    (7, 'Horaria')
]

class Metric(models.Model):
    metric = models.CharField( max_length=100, blank=False, null=False)
    format = models.IntegerField(choices = FORMAT, blank=False, null=False)
    name_table = models.CharField( max_length=100, blank=False, null=False, default='default')
    records_periodicity = models.IntegerField(choices=PERIODICITY, blank=False, null=False)


    class Meta:
        verbose_name = 'metric'
        ordering = ['metric']

        constraints = [
            models.UniqueConstraint(fields=["metric"], name='unique_Metric')
        ]        

    def __str__(self):
        return self.metric


PERIODS = [
    (1, 'Anual'),
    (2, 'Semestre 1'),
    (3, 'Semestre 2'),
    (4, 'Trimestre 1'),
    (5, 'Trimestre 2'),
    (6, 'Trimestre 3'),
    (7, 'Trimestre 4')
]


class UrlsFilesMetric(models.Model):
    url_file = models.URLField(max_length=200, blank=True, null=False, unique=True)
    year_file = models.IntegerField(blank=False)
    period = models.IntegerField(default=1, choices=PERIODS)
    last_update = models.DateTimeField(blank=True, null=True)
    processing_time = models.FloatField(blank=True, null=True)
    metric = models.ForeignKey(Metric, on_delete = models.CASCADE)

    def seconds(self):
        
      
        if self.processing_time == None:
            return 0
        return int(self.processing_time)

    def __str__(self):
        period = self.get_period_display()
        return f'{self.year_file} {period}'


class UrlsFilesMetricTask(models.Model):
    metric = models.ForeignKey(UrlsFilesMetric, related_name='tasks', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    seconds =  models.IntegerField(blank=False)
    has_error = models.BooleanField(default=False, blank=False, null=False)


class Component(models.Model):
    component = models.CharField(max_length=100, blank=False, null=False, unique=True)
    name_column = models.CharField(max_length=100, blank=False, null=False)
    metric = models.ForeignKey(Metric, on_delete = models.CASCADE)
    unit = models.CharField(max_length=100, blank=False, null=True)

    class Meta:
        verbose_name = 'metric'
        ordering = ['metric']

        constraints = [
            models.UniqueConstraint(fields=["component"], name='unique_Component')
        ]      


# --------------------------------------------------------------------
# Relational elements ------------------------------------------------
# --------------------------------------------------------------------
class Agent(models.Model):
    name = models.CharField(max_length=10, blank=True, null=False, unique=True, default='')
    detail = models.CharField(max_length=200, blank=True, null=True)
    activity = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    input_date = models.DateField(null=True)


class Ciiu(models.Model):
    name = models.CharField(max_length=200, blank=True, null=False, default='', unique=True)


class Fuel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, default='', unique=True)


class HydrologicalRegion(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, default='', unique=True)


class Market(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, default='', unique=True)    


class Resource(models.Model):
    """
    Ejecutar query del readme previamente, sin esto el agente 0 default no funcionara
    """
    name             = models.CharField(max_length=100, blank=True, null=False, default='')
    generation_type  = models.CharField(max_length=100, blank=True, null=False, default='')
    shipping_type    = models.CharField(max_length=100, blank=True, null=False, default='')
    is_minor         = models.CharField(max_length=100, blank=True, null=False, default='')
    is_autogenerator = models.CharField(max_length=100, blank=True, null=False, default='')
    clasification    = models.CharField(max_length=100, blank=True, null=False, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "generation_type", 
                                            "shipping_type", "is_minor", "is_autogenerator", 
                                            "clasification"], 
                                    name='unique_Resource'
            )
        ]


class River(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, default='', unique=True)


class SubActivity(models.Model):
    name = models.CharField(max_length=200, blank=True, null=False, default='', unique=True)


class Reservoir(models.Model):
    name = models.CharField(max_length=200, blank=True, null=False, default='', unique=True)




# --------------------------------------------------------------------
# Metrics ------------------------------------------------------------
# --------------------------------------------------------------------
# -------------------------------------------------------------------- Standard section
# -------------------------------------------------------------------- Standard section
# -------------------------------------------------------------------- Standard section


PHENOMENONS = [
    (1, 'Niña'),
    (2, 'Niño'),
]

class NationalBagPriceCustomDates(models.Model):
    # is male or female for every date, not both
    phenomenon = models.IntegerField(choices=PHENOMENONS)
    date = models.DateField(blank=False, null=False, unique=True)


    # def test(self):
    #     return  self.date.strftime('%m/%d/%Y')

    def __str__(self):
        phenomenon = self.get_phenomenon_display()
        return f'{self.date} {phenomenon}'


# Precio bolsa nacional
class NationalBagPrice(models.Model):
    date = models.DateField(unique=True)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)


# Demanda energia SIN
class EnergyDemandSIN(models.Model):
    date = models.DateField(unique=True)

    energy_demand_sin = models.FloatField(null=True)
    generation = models.FloatField(null=True)
    demand_not_attended = models.FloatField(null=True)
    exports = models.FloatField(null=True)
    imports = models.FloatField(null=True)

    class Meta:
        verbose_name = 'EnergyDemand'
        ordering = ['date']

    def __str__(self):
        return self.date


# En generacion cambia todo menos el tipo de generacion
class Generation(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent", "fuel"], name='unique_Generation')
        ]


# Metric: Maximo precio de oferta nacional
class MaximumNationalOfferPrice(models.Model):
    date = models.DateField(unique=True)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)


# Capacidad efectiva neta
class NetEffectiveCapacity(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)

    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE, null=False)
    net_effective_capacity = models.FloatField(null=True)

    class Meta:
        verbose_name = 'NetEffectiveCapacity'
        ordering = ['date']

        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent", "fuel"], name='unique_NetEffectiveCapacity')
        ]

    def __str__(self):
        return str(self.date)


# Metric: Precio de oferta
class OfferPrice(models.Model):
    date = models.DateField(null=False)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    ideal_offer_price = models.FloatField(null=True)
    shipping_offer_price = models.FloatField(null=True)
    declared_offer_price = models.FloatField(null=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_OfferPrice')
        ]        




# -------------------------------------------------------------------- Query section
# -------------------------------------------------------------------- Query section
# -------------------------------------------------------------------- Query section
"""
    Protocol for add a new metric:
    1. Add models to database, take care with the unique constraint between date and 
       relational elements, a error here will generate "there is no unique or exclusion 
       constraint matching the ON CONFLICT specification" exception when 
       you import data.
    2. Add metric to database
    3. Add components to database
    4. Add files to urlsfilesmetric

    5. This file have a new entity? 
       - Add to dct_col2table_relation, dct_relations_data2relations_db and
         dct_res_cols_data2res_cols_db in BaseParser

       - Run column_relation_view for import elements, this only apply for
         simple entities as Reservoir and market. Add new entities as Agent and Resources
         require implement very specific code, good luck.

    6. This file have a special format? implement in the code
"""

# AGC_Programado_(kWh)
class ScheduledAGC(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)


    class Meta:

        # unique_together = ("date", "resource", "fuel")

        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_ScheduledAGC')
        ]


# Aportes_diario
class DailyContributions(models.Model):
    date = models.DateField()
    hydrological_region = models.ForeignKey(HydrologicalRegion, on_delete=models.CASCADE, null=False)
    river = models.ForeignKey(River, on_delete=models.CASCADE, null=False)

    flow_inputs = models.FloatField(null=True)
    energy_contributions = models.FloatField(null=True)
    contributions = models.FloatField(null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "hydrological_region", "river"], name='unique_DailyContributions')
        ]            

    def __str__(self):
        return str(self.date)


# Compras de bolsa internacional
class InternationalBagShopping(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=["date", "agent"], name='unique_InternationalBagShopping')
        ]


# Compras de bolsa nacional
class NationalBagShopping(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=["date", "agent"], name='unique_NationalBagShopping')
        ]        


# Compras de bolsa TIE
class TIEBagShopping(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "agent"], name='unique_TIEBagShopping')
        ]


# Compras de contrato
class ContractPurchases(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "agent"], name='unique_ContractPurchases')
        ]


# Consumo de combustible
class FuelConsumption(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE, null=False)
    fuel_consumption = models.FloatField(null=True)

    class Meta:
        verbose_name = 'FuelConsumption'

        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent", "fuel"], name='unique_FuelConsumption')
        ]


# Costo marginal despacho programado
class MarginalCostScheduledDispatch(models.Model):
    date = models.DateField(unique=True)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)


# Delta internacional y delta nacional
class InternationalDeltaAndNationalDelta(models.Model):
    date = models.DateField(unique=True)
    international_delta = models.FloatField(null=True)
    national_delta = models.FloatField(null=True)


# Demanda comercial no regulada por CIIU
class CommercialDemandNotRegulatedByCIIU(models.Model):
    date = models.DateField()
    ciiu = models.ForeignKey(Ciiu, on_delete=models.CASCADE, null=False)
    subactivity = models.ForeignKey(SubActivity, on_delete=models.CASCADE, null=False)

    commercial_demand = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "ciiu", "subactivity"], name='unique_CommercialDemandNotRegulatedByCIIU')
        ]


# Demanda comercial por comercializador
class CommercialDemandPerMarketer(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "agent", "market"], name='unique_CommercialDemandPerMarketer')
        ]


# Demanda maxima de potencia
class MaximumPowerDemand(models.Model):
    date = models.DateField(unique=True)
    maximum_power_demand = models.FloatField(null=True)


# Demanda por OR
class DemandByOR(models.Model):
    date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "agent"], name='unique_DemandByOR')
        ]


# Desviaciones
class Deviations(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_Deviations')
        ]


# Disponibilidad real
class RealAvailability(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_RealAvailability')
        ]    


# Generacion de seguridad
class SecurityGeneration(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_SecurityGeneration')
        ]    


# Generacion ideal
class IdealGeneration(models.Model):
    date = models.DateField()
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=False)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "resource", "agent"], name='unique_IdealGeneration')
        ]    


# Precio Bolsa TIE
class TIEBagPrice(models.Model):
    date = models.DateField(unique=True)
    hour_0 = models.FloatField(null=True)
    hour_1 = models.FloatField(null=True)
    hour_2 = models.FloatField(null=True)
    hour_3 = models.FloatField(null=True)
    hour_4 = models.FloatField(null=True)
    hour_5 = models.FloatField(null=True)
    hour_6 = models.FloatField(null=True)
    hour_7 = models.FloatField(null=True)
    hour_8 = models.FloatField(null=True)
    hour_9 = models.FloatField(null=True)
    hour_10 = models.FloatField(null=True)
    hour_11 = models.FloatField(null=True)
    hour_12 = models.FloatField(null=True)
    hour_13 = models.FloatField(null=True)
    hour_14 = models.FloatField(null=True)
    hour_15 = models.FloatField(null=True)
    hour_16 = models.FloatField(null=True)
    hour_17 = models.FloatField(null=True)
    hour_18 = models.FloatField(null=True)
    hour_19 = models.FloatField(null=True)
    hour_20 = models.FloatField(null=True)
    hour_21 = models.FloatField(null=True)
    hour_22 = models.FloatField(null=True)
    hour_23 = models.FloatField(null=True)


# Precios Mensuales
class MonthlyPrices(models.Model):
    date = models.DateField(unique=True)
    price_shortage = models.FloatField(null=True)
    mc             = models.FloatField(null=True)
    cere           = models.FloatField(null=True)
    cee            = models.FloatField(null=True)
    fazni_price    = models.FloatField(null=True)
    average_contract_price               = models.FloatField(null=True)
    average_price_regulated_contracts    = models.FloatField(null=True)
    average_price_nonregulated_contracts = models.FloatField(null=True)


# Reservas Mensual
class MonthlyReserves(models.Model):
    date                = models.DateField(null=False)
    hydrological_region = models.ForeignKey(HydrologicalRegion, on_delete=models.CASCADE, null=False)
    reservoir           = models.ForeignKey(Reservoir, on_delete=models.CASCADE, null=False)

    useful_capacity_volume          = models.FloatField(null=True)
    maximum_technical_volume_energy = models.FloatField(null=True)
    useful_capacity_energy          = models.FloatField(null=True)
    useful_daily_volume             = models.FloatField(null=True)
    daily_useful_volume_energy      = models.FloatField(null=True)
    useful_dailyvolume              = models.FloatField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "hydrological_region", "reservoir"], 
                                    name='unique_MonthlyReserves')
        ]    