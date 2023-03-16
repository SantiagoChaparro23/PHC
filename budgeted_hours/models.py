from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Client(models.Model):
    client = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Client'
        ordering = ['client']

    def __str__(self):
        return str(self.client)


class ServiceType(models.Model):
    service_type = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Service type'
        ordering = ['id']

    def __str__(self):
        return str(self.service_type)


class Activities(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, blank=False, null=False)
    activity = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=700, blank=True, null=True)

    class Meta:
        verbose_name = 'Activities'
        ordering = ['service_type']

    def __str__(self):
        return str(self.service_type)


STATES = [
    (1, 'Pendiente'),
    (2, 'Aprobado'),
    (3, 'No aprobado')
]

STAGES = [
    (1, 'En revisión comercial'),
    (2, 'En revisión técnica'),
    (3, 'En revisión financiero'),
    (4, 'Finalizado')
]

PROJECTS = [
    (1, 'Proyecto corta duración'),
    (2, 'Proyecto media duración'),
    (3, 'Proyecto larga duración')
]

DEPENDS = [
    (1, 'Contrato'),
    (2, 'Reunión de Inicio'),
    (3, 'Otro')
]


class BudgetedHours(models.Model):
    code = models.CharField(max_length=15, blank=False, null=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=False, null=False)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, blank=False, null=False)
    value = models.IntegerField(default=0, blank=True, null=True)
    additional_costs = models.IntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    state = models.IntegerField(choices=STATES, default=1, blank=False, null=False)
    stages = models.IntegerField(choices=STAGES, default=1, blank=False, null=False)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    document_url = models.CharField(max_length=250, blank=True, null=True)
    start_at = models.DateField(blank=False, null=False)
    compromise_delivery_at = models.DateField(blank=False, null=False)
    duration_deliverables = models.TextField(max_length=2000, blank=True, null=True)
    contract_signed = models.BooleanField(default=None, blank=True, null=True)
    project_type = models.IntegerField(choices=PROJECTS, blank=True, null=True)
    project_depends = models.IntegerField(choices=DEPENDS, blank=True, null=True)
    category_version = models.ForeignKey('CategoriesVersions', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Budgeted Hours'
        ordering = ['code']

    def __str__(self):
        return str(self.code)


class BudgetedHoursFiles(models.Model):
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    file = models.CharField(max_length=255, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    files = models.TextField(blank=True, null=True)


class BudgetedHoursHistory(models.Model):
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Budgeted Hours History'
        ordering = ['-id']

    def __str__(self):
        return str(self.budgeted_hours)


class BudgetedHoursHistoryData(models.Model):
    budgeted_hours_history = models.ForeignKey(BudgetedHoursHistory, on_delete=models.CASCADE, blank=False, null=False)
    code = models.CharField(max_length=15, blank=False, null=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=False, null=False)
    value = models.IntegerField(default=0, blank=True, null=True)
    additional_costs = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Budgeted Hours History Data'
        ordering = ['-id']

    def __str__(self):
        return str(self.budgeted_hours_history)


class Categories(models.Model):
    category = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Categories'
        ordering = ['id']

    def __str__(self):
        return str(self.category)


class BudgetedHoursCategories(models.Model):
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, blank=False, null=False)
    value = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Budgeted hours categories'
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class CategoriesVersions(models.Model):
    budgeted_hours_categories = models.ForeignKey(BudgetedHoursCategories, on_delete=models.CASCADE, blank=False, null=False)
    version = models.IntegerField(default = 1, blank = False, null = False)

    class Meta:
        verbose_name = 'Versions'
        ordering = ['budgeted_hours_categories']

    def __str__(self):
        return str(self.version)


class Softwares(models.Model):
    software = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Softwares'
        ordering = ['id']

    def __str__(self):
        return str(self.software)


class Operator(models.Model):
    operator = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Operator'
        ordering = ['operator']

    def __str__(self):
        return str(self.operator)


class TemplatesBudgetedHours(models.Model):
    template_name = models.CharField(max_length= 100, blank=False, null=False)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, blank=False, null=False)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Templates'
        ordering = ['template_name']

    def __str__(self):
        return str(self.template_name)


class HoursTemplates(models.Model):
    templates_budgeted_hours = models.ForeignKey(TemplatesBudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, blank=False, null=False)
    software = models.ForeignKey(Softwares, on_delete=models.CASCADE, blank=True, null=True)
    engineer = models.FloatField(default=0)
    leader = models.FloatField(default=0)
    management = models.FloatField(default=0)
    software_hours = models.FloatField(default=0)
    external = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Hours Templates'
        ordering = ['templates_budgeted_hours']

    def __str__(self):
        return str(self.templates_budgeted_hours)


class Hours(models.Model):
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, blank=False, null=False)
    category = models.ForeignKey(Categories, related_name="hours", on_delete=models.CASCADE, blank=False, null=False)
    software = models.ForeignKey(Softwares, on_delete=models.CASCADE, blank=True, null=True)
    engineer = models.FloatField(default=0)
    leader = models.FloatField(default=0)
    senior_leader = models.FloatField(default=0)
    management = models.FloatField(default=0)
    software_hours = models.FloatField(default=0)
    external = models.FloatField(default=0)
    category_version = models.ForeignKey(CategoriesVersions, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = 'Hours'
        ordering = ['budgeted_hours']

    def __str__(self):
        return str(self.budgeted_hours)


# class HoursHistory(models.Model):
#     hours = models.ForeignKey(Hours, on_delete=models.CASCADE, blank=False, null=False)
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
#     updated_at = models.DateTimeField(auto_now=True)


class TraceabilityBudgetedHours(models.Model):
    budgeted_hours = models.OneToOneField(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Traceability'
        ordering = ['budgeted_hours']

    def __str__(self):
        return str(self.budgeted_hours)


class TraceabilityBudgetedHoursHistory(models.Model):
    budgeted_hours = models.ForeignKey(TraceabilityBudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    reviewed_at = models.DateTimeField(auto_now=True)
    stages = models.IntegerField(choices=STAGES, default=1, blank=False, null=False)

    class Meta:
        verbose_name = 'Traceability Budgeted Hours History'
        ordering = ['-id']

    def __str__(self):
        return str(self.budgeted_hours)


ANSWER = [
    (1, 'Sí'),
    (2, 'No'),
]


class PriceRequestFormat(models.Model):
    budgeted_hours = models.OneToOneField(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    aa = models.CharField(max_length=100, blank=True, null=True) # Códigos de proyectos de Referencia
    ab = models.CharField(max_length=100, blank=True, null=True) # Valores cotizados al mismo cliente para proyectos similares
    ac = models.CharField(max_length=100, blank=True, null=True) # Tiempos presupuestados vs ejecutados en proyectos similares
    ad = models.CharField(max_length=100, blank=True, null=True) # ¿Cómo llegó el cliente a phc? (ejemplo: referido, ferias, internet, etc)
    ae = models.CharField(max_length=100, blank=True, null=True) # Descripción Breve del cliente
    af = models.CharField(max_length=100, blank=True, null=True) # Moneda en la que se debe entregar la cotización
    ag = models.CharField(max_length=100, blank=True, null=True) # Nombre de Operador de Red si aplica
    ah = models.CharField(max_length=100, blank=True, null=True) # ¿Se necesita póliza para este proyecto?
    ai = models.CharField(max_length=100, blank=True, null=True) # ¿Se requiere la participación de un especialista externo? Escribir el nombre y Valor
    aj = models.CharField(max_length=100, blank=True, null=True) # ¿Se requieren Gastos de viajes para el proyecto?
    ak = models.CharField(max_length=100, blank=True, null=True) # Tiempo de elaboración de la propuesta
    al = models.CharField(max_length=100, blank=True, null=True) # Personas que participarían en la ejecución del proyecto
    am = models.CharField(max_length=100, blank=True, null=True) # ¿Existe algún impuesto o Gasto adicional para la propuesta?

    ba = models.IntegerField(choices = ANSWER, blank=True, null=True) # Cámara de Comercio  Actualizada
    bb = models.IntegerField(choices = ANSWER, blank=True, null=True) # Registro Mercantil Renovado
    bc = models.IntegerField(choices = ANSWER, blank=True, null=True) # Fecha de constitución de la Empresa mayor a 5 años
    bd = models.IntegerField(choices = ANSWER, blank=True, null=True) # Duración de la Sociedad Indefinida
    be = models.IntegerField(choices = ANSWER, blank=True, null=True) # Objeto y Actividad social acorde con el proyecto solicitado
    bf = models.IntegerField(choices = ANSWER, blank=True, null=True) # Análisis positivos de los antecedentes del Representante Legal
    bg = models.IntegerField(choices = ANSWER, blank=True, null=True) # Formulario del conocimiento del cliente completo
    bh = models.IntegerField(choices = ANSWER, blank=True, null=True) # Cuenta con Estados Financieros o Impuesta de Renta Vigentes

    ca = models.IntegerField(choices = ANSWER, blank=True, null=True) # La búsqueda del RL y relacionados se encuentran en la lista de la OFAC
    cb = models.IntegerField(choices = ANSWER, blank=True, null=True) # La búsqueda del RL y relacionados se encuentran en la lista de la ONU
    cc = models.IntegerField(choices = ANSWER, blank=True, null=True) # La búsqueda del RL y relacionados se encuentran involucrados en NOTICIAS PÚBLICAS que impliquen un riesgo alto para nuestra empresa

    class Meta:
        verbose_name = 'Price Request Format'
        ordering = ['budgeted_hours']

    def __str__(self):
        return str(self.budgeted_hours)
