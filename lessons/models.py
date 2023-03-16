from django.db import models
from django.contrib.auth.models import User
from budgeted_hours.models import Client, BudgetedHours


# Create your models here.
LESSON_TYPE = [
    (1, 'Técnica'),
    (2, 'Gestión del proyecto'),
    (3, 'General')
]


class ElectricalStudies(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateField(blank=False, null=False)
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    lesson_type = models.IntegerField(choices=LESSON_TYPE, blank=False, null=False)
    action_plan = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='static/static/lessons/electrical_studies', blank=True, null=True)

    class Meta:
        verbose_name = 'Electrical studies'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.budgeted_hours)


class Consultancies(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateField(blank=False, null=False)
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    lesson_type = models.IntegerField(choices=LESSON_TYPE, blank=False, null=False)
    action_plan = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='static/static/lessons/consultancies', blank=True, null=True)

    class Meta:
        verbose_name = 'Consultancies'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.budgeted_hours)


SUBCATEGORY = [
    (1, 'Función de protección'),
    (2, 'Simulación'),
    (3, 'Informe'),
    (4, 'Otro')
]

ELEMENT_TYPE = [
    (1, 'Generador fotovoltaico'),
    (2, 'Generador hidráulico'),
    (3, 'Subestación de transmisión'),
    (4, 'Subestación de distribución'),
    (5, 'Generador térmico'),
    (6, 'Generador eólico'),
    (7, 'Transformador'),
    (8, 'Barra'),
    (9, 'Línea'),
    (10, 'Otro')
]

RELAY_BRAND = [
    (1, 'Siemens'),
    (2, 'GE'),
    (3, 'ABB'),
    (4, 'SEL'),
    (5, 'Schneider'),
    (6, 'ZIV'),
    (7, 'Fusible'),
    (8, 'CB'),
    (9, 'General'),
    (10, 'Otro')
]


class ProtectionCoordinationStudies(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateField(blank=False, null=False)
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    lesson_type = models.IntegerField(choices=LESSON_TYPE, blank=False, null=False)
    action_plan = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subcategory = models.IntegerField(choices=SUBCATEGORY, blank=True, null=True)
    subcategory_description = models.CharField(max_length=100, blank=True, null=True)
    element_type = models.IntegerField(choices=ELEMENT_TYPE, blank=True, null=True)
    element_type_description = models.CharField(max_length=100, blank=True, null=True)
    protection = models.CharField(max_length=255, blank=True, null=True)
    relay_brand = models.IntegerField(choices=RELAY_BRAND, blank=True, null=True)
    relay_brand_description = models.CharField(max_length=100, blank=True, null=True)
    relay_model = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='static/static/lessons/protection_coordination_studies', blank=True, null=True)

    class Meta:
        verbose_name = 'Protection coordination studies'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.budgeted_hours)


class Zones(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Operators(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    zone = models.ForeignKey(Zones, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = "Operator"
        verbose_name_plural = "Operators"
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Areas(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    operator = models.ForeignKey(Operators, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def zone(self):
        return self.operator.zone


SUBCATEGORY_2 = [
    (1, 'Ajuste de la base de datos'),
    (2, 'Revisión de la información'),
    (3, 'Análisis'),
    (4, 'Informe y anexos')
]


class ConnectionStudies(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateField(blank=False, null=False)
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    zone = models.ForeignKey(Zones, on_delete=models.CASCADE, blank=False, null=False)
    operator = models.ForeignKey(Operators, on_delete=models.CASCADE, blank=False, null=False)
    area = models.ForeignKey(Areas, on_delete=models.CASCADE, blank=False, null=False)
    lesson_type = models.IntegerField(choices=LESSON_TYPE, blank=False, null=False)
    subcategory = models.IntegerField(choices=SUBCATEGORY_2, blank=True, null=True)
    action_plan = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='static/static/lessons/connection_studies', blank=True, null=True)

    # description = models.TextField( blank=True, null=True)
    # date = models.DateField(blank=False, null=False)
    # code = models.CharField(max_length=255, blank=True, null=False)
    # responsable = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    # created_by = models.ForeignKey(User, related_name='created_by', on_delete=models.CASCADE, null=False)
    # type = models.ForeignKey(LessonType, on_delete=models.CASCADE, null=False)
    # file  = models.FileField(upload_to="static/connection_studies", null=True, blank=True)

    class Meta:
        verbose_name = "Connection studies"
        ordering = ['-created_at']

    def __str__(self):
        return str(self.budgeted_hours)

    def get_filename(self):
        w = self.file.url.split('/')
        if len(w):
            return w[-1]

        return 'Ver archivo'


STUDY_TYPE = [
    (1, 'Estudio de mercado'),
    (2, 'Proyección de precios'),
    (3, 'Estudios energéticos - Estudios de conexión'),
    (4, 'Asesoría')
]


class MarketStudies(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateField(blank=False, null=False)
    budgeted_hours = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    study_type = models.IntegerField(choices=STUDY_TYPE, blank=True, null=True)
    lesson_type = models.IntegerField(choices=LESSON_TYPE, blank=False, null=False)
    subcategory = models.IntegerField(choices=SUBCATEGORY_2, blank=True, null=True)
    action_plan = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='static/static/lessons/market_studies', blank=True, null=True)

    class Meta:
        verbose_name = "Market studies"
        ordering = ['-created_at']

    def __str__(self):
        return str(self.budgeted_hours)

    def get_filename(self):
        w = self.file.url.split('/')
        if len(w):
            return w[-1]


################################################################################

# class LessonType(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False)
#     def __str__(self):
#         return str(self.name)

#     class Meta:
#         verbose_name = "Tipo de lección"
#         verbose_name_plural = "Tipo de lecciónes"


# class StudyType(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False)

#     def __str__(self):
#         return str(self.name)


#     class Meta:
#         ordering = ('-name',)
#         verbose_name = "Tipo de estudio"
#         verbose_name_plural = "Tipo de estudios"

# class InformationType(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False)
#     study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE, null=False, default=0)
    
#     def __str__(self):
#         return str(self.name)

#     class Meta:
#         ordering = ('name',)
#         verbose_name = "Tipo de información"
#         verbose_name_plural = "Tipo de informaciones"


# class Characteristic(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False)
#     information_type = models.ForeignKey(InformationType, on_delete=models.CASCADE, null=False, default=0)
#     has_other = models.BooleanField(default=False, blank=False, null=False)

    
#     class Meta:
#         ordering = ('has_other', 'name')
#         verbose_name = "Característica"
#         verbose_name_plural = "Características"

#     def study_type(self):
#         return self.information_type.study_type


#     def __str__(self):
#         return str(self.name)



# TYPES = [
#     (1, 'Revision de demanda'),
#     (2, 'Precios de combustibles'),
#     (3, 'Plan de expansion'),
# ]



# def update_filename(instance, filename):
  
  
#     split = filename.split(".")
#     ext = split[-1]
#     unix = int(datetime.now().timestamp())
  
#     path = "static/market_studies/files"
#     format = f'{instance.pk}-{unix}.{ext}'
#     return os.path.join(path, format)



# class MarketStudiesFiles(models.Model):   
#     file = models.CharField(max_length=255, blank=True, null=True)
#     file_name = models.CharField(max_length=255, blank=True, null=True)
#     type_file = models.IntegerField(choices=TYPES,  null=True, blank=True)
#     files = models.TextField( blank=True, null=True)

#     def get_type(self):
#         return self.get_type_file_display()


# # Commercial lessons -------------------------------------------------------
# class RelatedArea(models.Model):
#     name = models.CharField(max_length=500, blank=False, null=False)


# class Commercial(models.Model):
#     # Principal elements
#     date = models.DateField(blank=False, null=False)
#     business_manager = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE, related_name='business_manager')
#     client = models.ForeignKey(Client, blank=False, null=False, on_delete=models.CASCADE)
#     phc_code = models.CharField(max_length=255, blank=True, null=False)
#     service_type = models.ForeignKey(ServiceType, null=False, on_delete=models.CASCADE)

#     # Extra information
#     rfp_issued_by_client = models.BooleanField(blank=False, null=False)
#     name = models.CharField(max_length=255, blank=True, null=True)


# class PreventiveActions(models.Model):
#     commercial = models.ForeignKey(Commercial, null=False, on_delete=models.CASCADE)
#     description = models.CharField(max_length=2000, blank=False, null=False)
        

# class CommercialLesson(models.Model):
#     commercial = models.ForeignKey(Commercial, null=False, on_delete=models.CASCADE)
#     general = models.CharField(max_length=1000, blank=False, null=False)
#     description = models.CharField(max_length=2000, blank=False, null=True)
#     positive = models.BooleanField(default=False, blank=False, null=False)


# #   Relational tables
# class PreventiveActionsCommercialLesson(models.Model):
#     preventive_action = models.ForeignKey(PreventiveActions, null=False, on_delete=models.CASCADE)
#     commercial_lesson = models.ForeignKey(CommercialLesson, null=False, on_delete=models.CASCADE)


# class CommercialRelatedArea(models.Model):
#     commercial = models.ForeignKey(Commercial, null=False, on_delete=models.CASCADE)
#     related_area = models.ForeignKey(RelatedArea, null=False, on_delete=models.CASCADE)


# class CommercialUser(models.Model):
#     user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
#     commercial = models.ForeignKey(Commercial, null=False, on_delete=models.CASCADE)






        