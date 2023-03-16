from django.contrib.auth.models import User
from budgeted_hours.models import Activities, BudgetedHours
from django.db import models
import math

# Create your models here.
class ReportedHours(models.Model):
    code = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    report_date_at = models.DateField(auto_now=False, blank=False, null=False)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, blank=False, null=False)
    time = models.IntegerField(blank=False, null=False)
    description = models.TextField(max_length=250, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reported Hours'
        ordering = ['code']

    def __str__(self):
        return str(self.code)
        


    def format_minutes(self):

        hours = self.time // 60
        hours = math.floor(hours)
        minutes = self.time % 60

        minutes = "{:02d}".format(minutes)
        hours = "{:02d}".format(hours)
        return f'{hours}:{minutes}'


class UserToReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class ReportedHoursDraft(models.Model):
    code = models.ForeignKey(BudgetedHours, on_delete=models.CASCADE, blank=False, null=False)
    report_date_at = models.DateField(auto_now=False, blank=False, null=False)
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, blank=False, null=False)
    time = models.IntegerField(blank=False, null=False)
    description = models.TextField(max_length=250, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True, related_name='reported_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reported Hours'
        ordering = ['code']

    def __str__(self):
        return str(self.code)


    def format_date(self):
        return self.report_date_at.strftime('%Y-%m-%d')

    def format_minutes(self):

        hours = self.time // 60
        hours = math.floor(hours)
        minutes = self.time % 60

        minutes = "{:02d}".format(minutes)
        hours = "{:02d}".format(hours)
        return f'{hours}:{minutes}'