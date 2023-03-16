from django.contrib import admin

# Register your models here.
from users.models import Roles, RolesUsers

class RolesUsersAdmin(admin.ModelAdmin):
    list_display = (
        'role',
        'user'
    )
    

admin.site.register(Roles)
admin.site.register(RolesUsers, RolesUsersAdmin )
