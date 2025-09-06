from django.contrib import admin
from .models import JobPosting


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'company', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
