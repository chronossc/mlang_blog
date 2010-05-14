from django.contrib import admin
from models import *

class BObjectTypeAdmin(admin.ModelAdmin):
    pass

class BObjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(BObject,BObjectAdmin)
admin.site.register(BObjectType,BObjectTypeAdmin)
