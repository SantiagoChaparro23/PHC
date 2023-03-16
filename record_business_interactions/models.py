from django.db import models

from budgeted_hours.models import Client
from django.contrib.auth.models import User


# Create your models here.
class InteractionType(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)


class VisitRecord(models.Model):

    date_record = models.DateTimeField()
    date_visit = models.DateField(null=False)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    phc_code = models.CharField(default='', max_length=100, blank=True, null=False)

    interaction_type = models.ForeignKey(InteractionType, on_delete=models.CASCADE, null=False)
    customer_commitments = models.CharField(default='', max_length=100, blank=True, null=False)

    is_in_crm = models.BooleanField(default=False, blank=False, null=False)
    validated_in_crm = models.BooleanField(default=None, null=True)


    class Meta:
        pass

class Settings(models.Model):

    key = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=100)
