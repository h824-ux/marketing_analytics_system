from django.contrib import admin
from .models import *

admin.site.register(Feedback)
admin.site.register(RequestSupport)

class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset_name', 'upload_date')
    list_filter = ('upload_date',)
    search_fields = ('name', 'dataset_name', 'description')