from django.contrib import admin

from .models import UserToReport




class UserToReportAdmin(admin.ModelAdmin):
    ordering = ('user',)
    
    



admin.site.register(UserToReport, UserToReportAdmin)
