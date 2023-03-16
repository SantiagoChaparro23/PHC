from django.contrib import admin

# Register your models here.
from record_business_interactions.models import Settings

class SettingsAdmin(admin.ModelAdmin):
    list_display = (
        'key',
        'value'
    )

admin.site.register(Settings, SettingsAdmin)
