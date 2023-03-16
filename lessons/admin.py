from django.contrib import admin

from .models import Zones, Operators, Areas#, ConnectionStudies, StudyType, InformationType, Characteristic, MarketStudies


class ZoneAdmin(admin.ModelAdmin):
    pass

class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone')

class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'operator', 'zone')


# class ConnectionStudiesAdmin(admin.ModelAdmin):
#     pass




# class StudyTypeAdmin(admin.ModelAdmin):
#     pass

# class InformationTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'study_type')


# class CharacteristicAdmin(admin.ModelAdmin):
#     list_display = ('name', 'information_type', 'study_type')

# class MarketStudiesAdmin(admin.ModelAdmin):
#     pass

admin.site.register(Zones, ZoneAdmin)
admin.site.register(Operators, OperatorAdmin)
admin.site.register(Areas, AreaAdmin)
# admin.site.register(ConnectionStudies, ConnectionStudiesAdmin)



# admin.site.register(StudyType, StudyTypeAdmin)
# admin.site.register(InformationType, InformationTypeAdmin)
# admin.site.register(Characteristic, CharacteristicAdmin)
# admin.site.register(MarketStudies, MarketStudiesAdmin)