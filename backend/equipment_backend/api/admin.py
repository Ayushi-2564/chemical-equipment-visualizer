# api/admin.py
from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'upload_date', 'total_count', 
                    'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['upload_date', 'user']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['upload_date']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 
                    'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name', 'equipment_type']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('dataset')