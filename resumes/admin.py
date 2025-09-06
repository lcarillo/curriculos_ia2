from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'file_type', 'status', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['user__username', 'file_name']
    readonly_fields = ['created_at', 'updated_at']
