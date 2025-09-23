from django.contrib import admin
from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'resume', 'job', 'score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'resume__file_name', 'job__title']
    readonly_fields = ['created_at', 'updated_at']