from django.contrib import admin
from app import models

class FirstCatalogAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.FirstCatalog, FirstCatalogAdmin)

class SecondCatalogAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.SecondCatalog, SecondCatalogAdmin)
