from django.contrib import admin
from imports.models import NationalBagPriceCustomDates

class AuthorAdmin(admin.ModelAdmin):
    pass
admin.site.register(NationalBagPriceCustomDates, AuthorAdmin)