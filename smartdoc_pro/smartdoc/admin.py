from django.contrib import admin
from . import models

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','create_date',
                    'mod_date','name','code','author_id']


admin.site.register(models.Product,ProductAdmin)

admin.site.register(models.Category)

admin.site.register(models.Document)