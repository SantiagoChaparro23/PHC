from django.contrib import admin
from django.db.models.base import Model

# Register your models here.
from budgeted_hours.models import ServiceType
# from budgeted_hours.forms.budgeted_hours_form import BudgetedHoursForm

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = (
        'service_type',
        'id'
    )


# class BudgetedHoursAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at',)
#     form = BudgetedHoursForm


admin.site.register(ServiceType, ServiceTypeAdmin)