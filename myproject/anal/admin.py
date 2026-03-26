from django.contrib import admin
from .models import Dataset

admin.site.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset_name', 'upload_date')
    list_filter = ('upload_date',)
    search_fields = ('name', 'dataset_name', 'description')

